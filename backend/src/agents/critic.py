import json
import pandas as pd
from typing import Optional, Dict, Any, List
from src.agents.base import BaseAgent, AgentValidationException
import logging

class ValidationCritic(BaseAgent):
    def __init__(self):
        super().__init__()
        
    def validate_and_score(self, model: str, raw_llm_json: Dict[str, Any], candidates_df: pd.DataFrame, qualitative_preferences: Optional[str]) -> Dict[str, Any]:
        """
        Validates output against hallucinations and uses LLM to assign a quality score (RQS).
        """
        recs = raw_llm_json.get("raw_recommendations", [])
        if not recs:
            raise AgentValidationException("No recommendations were returned in the 'raw_recommendations' array.", "CRITICAL: You returned an empty array. You must return ALL candidates.")

        # 1. Programmatic Hallucination Check
        valid_names = set(candidates_df['restaurant_name'].unique())
        for r in recs:
            name = r.get("restaurant_name")
            if name not in valid_names:
                logging.warning(f"ValidationCritic caught Hallucination: {name}")
                raise AgentValidationException(
                    message=f"Hallucination Detected: {name}",
                    feedback_prompt=f"CRITICAL: You hallucinated the restaurant '{name}' which was NOT in the Candidate List. You MUST ONLY use the EXACT names from the Candidate List."
                )

        # 2. RQS (Recommendation Quality Score) Scoring via fast LLM
        prompt = f"""[System Persona]
You are an objective AI evaluator. Review the generated restaurant recommendations and the user's qualitative preferences.

[User Preferences]
{qualitative_preferences if qualitative_preferences else "Good food"}

[Generated Recommendations]
{json.dumps(recs, indent=2)}

[Task]
Assign a Recommendation Quality Score (RQS) from 1 to 5 based on how well the justifications actually address the user's qualitative preferences.
1 = Generic, unhelpful, or completely ignores preferences.
5 = Highly personalized, directly addresses the specific preferences.

Output strictly in JSON:
{{
  "rqs_score": <int>,
  "critic_notes": "<string explaining the score>"
}}
"""
        logging.info("ValidationCritic: Scoring recommendations...")
        evaluation = self._call_llm(model=model, prompt=prompt)
        
        rqs = 3 # Default safe score
        if evaluation:
            rqs = evaluation.get("rqs_score", 3)
            logging.info(f"ValidationCritic assigned RQS: {rqs}/5 - {evaluation.get('critic_notes', '')}")
            
        return {
            "validated_recommendations": recs,
            "rqs_score": rqs
        }
