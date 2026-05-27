import pandas as pd
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import time

from src.config import Config
from src.observability.logger import telemetry_logger
from src.observability.cache import prompt_cache
from src.agents.ranker import SemanticRanker
from src.agents.critic import ValidationCritic
from src.agents.synthesizer import SynthesisTrustAgent
from src.agents.comparator import ComparisonAgent
from src.agents.base import AgentValidationException
from src.memory.manager import MemoryManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class Recommendation(BaseModel):
    restaurant_name: str
    rank: int
    cuisine: str
    rating: float
    average_cost: float
    location: str
    estimated_cost_tier: str = Field(description="Low, Medium, or High")
    justification: str
    highlighted_features: list[str]

class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]

class Orchestrator:
    def __init__(self):
        self.cache_file = Config.CACHE_FILE
        self.df = self._load_data()
        self.ranker = SemanticRanker()
        self.critic = ValidationCritic()
        self.synthesizer = SynthesisTrustAgent()
        self.comparator = ComparisonAgent()
        self.memory = MemoryManager()
        
    def _load_data(self) -> pd.DataFrame:
        if not self.cache_file.exists():
            raise FileNotFoundError(f"Cache file {self.cache_file} not found. Please run ingestion first.")
        return pd.read_parquet(self.cache_file, engine='pyarrow')

    def filter_candidates(self, 
                          location: str, 
                          cuisine: Optional[str] = None, 
                          budget: Optional[str] = None, 
                          min_rating: float = 0.0):
        """
        Deterministically filters the dataset. Auto-widens search if 0 matches are found.
        Truncates to top MAX_CANDIDATES by popularity index.
        Returns: (candidates_df, widened_message)
        """
        location = location.lower().strip()
        filtered_df = self.df[self.df['location_clean'] == location].copy()
        
        if filtered_df.empty:
            logging.warning(f"No restaurants found in location: {location}. Relaxing location filter completely.")
            filtered_df = self.df.copy()
            
        # Helper function to apply remaining filters
        def apply_filters(df, c, b, r):
            mask = pd.Series(True, index=df.index)
            if c and c.lower() != "any":
                mask = mask & df['cuisines'].str.contains(c, case=False, na=False)
            if b and b.lower() != "any":
                mask = mask & (df['budget_tier'].str.lower() == b.lower())
            if r > 0.0:
                mask = mask & (df['rating'] >= r)
            return df[mask]

        candidates = apply_filters(filtered_df, cuisine, budget, min_rating)
        
        # Auto-Widening Strategy from edge-case.md
        widened_message = None
        if candidates.empty:
            logging.info("Zero matches found with strict filters. Auto-widening search by dropping rating...")
            candidates = apply_filters(filtered_df, cuisine, budget, 0.0)
            if not candidates.empty:
                widened_message = "No exact matches found. We dropped the minimum rating requirement to show you the best available options."
            
            if candidates.empty:
                logging.info("Still zero matches. Broadening budget tier constraint...")
                candidates = apply_filters(filtered_df, cuisine, None, 0.0)
                if not candidates.empty:
                    widened_message = "No exact matches found. We expanded the budget and rating requirements to find these options."
                
                if candidates.empty:
                    logging.info("Still zero matches. Broadening cuisine constraint...")
                    candidates = apply_filters(filtered_df, None, None, 0.0)
                    if not candidates.empty:
                        widened_message = "No exact matches found. We broadened the cuisine, budget, and rating filters to find the best spots nearby."
                        
                    
        # Token limit risk mitigation (Truncation)
        if not candidates.empty:
            candidates = candidates.copy()
            # Sort by a combination of rating and votes
            candidates['popularity_index'] = candidates['rating'] * candidates['votes']
            candidates = candidates.sort_values(by=['popularity_index', 'rating'], ascending=False)
            
            if len(candidates) > Config.MAX_CANDIDATES:
                logging.info(f"Truncating {len(candidates)} candidates down to Top {Config.MAX_CANDIDATES} to save token costs.")
                candidates = candidates.head(Config.MAX_CANDIDATES)
                
        return candidates, widened_message

    def get_llm_recommendations(self, candidates_df: pd.DataFrame, req, trace_id: str, widened_message: Optional[str] = None, session_id: Optional[str] = None) -> dict:
        """
        Multi-agent orchestration pipeline.
        """
        fallback_response = self._generate_fallback(candidates_df)
        
        # Fetch user memory profile
        user_memory = self.memory.get_user_profile(session_id) if session_id else ""
        
        # 1. Check Cache
        cache_hash = prompt_cache.generate_hash(req.location, req.cuisine, req.budget, req.min_rating, req.qualitative + user_memory)
        cached_data = prompt_cache.get(cache_hash)
        if cached_data:
            logging.info(f"Prompt Cache Hit for {cache_hash}. Serving instantly.")
            telemetry_logger.log_event(trace_id, "PROMPT_CACHE_HIT", {"hash": cache_hash})
            return {"recommendations": cached_data, "source": "LLM_Cached"}
        
        # 2. Cost-Aware Routing
        if req and req.qualitative and len(req.qualitative.strip()) > 10:
            target_model = Config.REASONING_MODEL
            logging.info("Complex query detected. Routing to REASONING_MODEL.")
        else:
            target_model = Config.FAST_MODEL
            logging.info("Simple query detected. Routing to FAST_MODEL.")
            
        location = req.location if req else "Unknown"
        cuisine = req.cuisine if req else "Any"
        qualitative = req.qualitative if req else ""
        
        # 3. Agent Pipeline Retry Loop
        max_retries = 2
        correction_prompt = None
        
        for attempt in range(max_retries + 1):
            logging.info(f"Agent Pipeline Attempt {attempt + 1}/{max_retries + 1}")
            
            # --- AGENT 1: Ranker ---
            start_llm = time.time()
            raw_json = self.ranker.rank_candidates(
                model=target_model,
                candidates_df=candidates_df,
                qualitative_preferences=req.qualitative,
                correction_prompt=correction_prompt,
                user_memory=user_memory
            )
            
            telemetry_logger.log_event(trace_id, "AGENT_RANKER_COMPLETE", {
                "model_used": target_model,
                "latency_ms": int((time.time() - start_llm) * 1000),
                "attempt": attempt + 1
            })
            
            if not raw_json:
                logging.error("Ranker Agent failed to return valid JSON.")
                telemetry_logger.log_event(trace_id, "FALLBACK_TRIGGERED", {"trigger_reason": "RANKER_FAILED"})
                return fallback_response
                
            # --- AGENT 2: Critic ---
            try:
                validated_data = self.critic.validate_and_score(
                    model=Config.FAST_MODEL, # Critic always uses the fast model
                    raw_llm_json=raw_json,
                    candidates_df=candidates_df,
                    qualitative_preferences=qualitative
                )
                
                telemetry_logger.log_event(trace_id, "AGENT_CRITIC_APPROVE", {
                    "rqs_score": validated_data.get("rqs_score")
                })
                
                # --- AGENT 3: Synthesizer ---
                final_output = self.synthesizer.synthesize_response(validated_data, widened_message, user_memory)
                
                # Save to cache
                if req:
                    prompt_cache.set(cache_hash, final_output["recommendations"])
                    
                return final_output
                
            except AgentValidationException as e:
                # Hallucination or Schema error caught by Critic!
                logging.warning(f"Validation Exception Caught: {str(e)}")
                telemetry_logger.log_event(trace_id, "AGENT_CRITIC_REJECT", {
                    "reason": "HALLUCINATION_DETECTED",
                    "attempt": attempt + 1
                })
                correction_prompt = e.feedback_prompt
                # Loop will retry!
                
        # If we exhausted retries
        logging.error("Agent pipeline exhausted retries. Falling back.")
        telemetry_logger.log_event(trace_id, "FALLBACK_TRIGGERED", {"trigger_reason": "RETRIES_EXHAUSTED"})
        return fallback_response

    def _generate_fallback(self, candidates_df: pd.DataFrame) -> dict:
        """Generates a deterministic response structure when LLM fails."""
        recs = []
        top = candidates_df.head(5)
        for idx, row in enumerate(top.to_dict(orient='records')):
            recs.append({
                "restaurant_name": row["restaurant_name"],
                "rank": idx + 1,
                "cuisine": row["cuisines"],
                "rating": row["rating"],
                "average_cost": row.get("average_cost", 0.0),
                "location": row.get("location", "Unknown"),
                "estimated_cost_tier": row["budget_tier"],
                "justification": "AI reasoning currently unavailable. This is a top-rated deterministic match.",
                "highlighted_features": ["Popular Choice"]
            })
        return {"recommendations": recs, "source": "Deterministic Fallback"}

    def compare_candidates(self, restaurant_names: List[str], qualitative_preferences: str, trace_id: str = "test-trace") -> dict:
        """
        Fetches the selected candidates from the dataframe and runs the ComparisonAgent.
        """
        # Fetch records from df matching names
        matches = self.df[self.df['restaurant_name'].isin(restaurant_names)]
        if matches.empty:
            logging.error("No valid restaurants found for comparison.")
            return {"comparisons": [], "verdict": "Invalid selection."}
            
        records = matches[['restaurant_name', 'location', 'cuisines', 'average_cost', 'rating', 'votes', 'budget_tier']].to_dict(orient='records')
        
        telemetry_logger.log_event(trace_id, "COMPARISON_REQUESTED", {
            "restaurant_count": len(records)
        })
        
        # Always use REASONING_MODEL for comparison to get better results and spread TPM across model buckets
        target_model = Config.REASONING_MODEL
        
        start_llm = time.time()
        result = self.comparator.generate_comparison(target_model, records, qualitative_preferences)
        
        telemetry_logger.log_event(trace_id, "COMPARISON_COMPLETE", {
            "model_used": target_model,
            "latency_ms": int((time.time() - start_llm) * 1000)
        })
        
        return result

def test_orchestrator():
    class DummyReq:
        location = "Delhi"
        cuisine = "Italian"
        budget = "Any"
        min_rating = 4.0
        qualitative = "A cozy place for a date"
        
    engine = Orchestrator()
    logging.info("Testing deterministic filtering for Delhi, Italian Cuisine")
    # Based on our mock data, The Big Chill has Italian and is in Delhi
    candidates, widened = engine.filter_candidates("Delhi", cuisine="Italian", budget=None, min_rating=4.0)
    
    logging.info(f"Found {len(candidates)} candidates.")
    for idx, row in candidates.iterrows():
        logging.info(f"- {row['restaurant_name']} ({row['rating']} stars, {row['budget_tier']} budget)")
        
    logging.info("Testing Multi-Agent LLM Integration Pipeline...")
    results = engine.get_llm_recommendations(candidates, req=DummyReq(), trace_id="test-trace", widened_message=widened)
    
    logging.info(f"Results Source: {results.get('source')}")
    logging.info(f"Confidence: {results.get('confidence_score')}")
    logging.info(str(results.get("recommendations"))[:500] + "...")

if __name__ == "__main__":
    test_orchestrator()
