from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
import uuid

from src.orchestrator import Orchestrator
from src.config import Config
from src.observability.logger import telemetry_logger

app = FastAPI(title="Zomato Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance to hold cached parquet
engine = None

@app.on_event("startup")
def startup_event():
    global engine
    try:
        engine = Orchestrator()
    except Exception as e:
        print(f"Error loading Orchestrator: {e}")

class RecommendRequest(BaseModel):
    location: str
    cuisine: str
    budget: str
    min_rating: float = 4.0
    qualitative: str = ""
    session_id: Optional[str] = None

class CompareRequest(BaseModel):
    restaurant_names: list[str]
    qualitative: Optional[str] = ""

class FeedbackRequest(BaseModel):
    session_id: str
    trace_id: str
    restaurant_name: str
    cuisine: Optional[str] = ""
    budget_tier: Optional[str] = ""
    is_positive: bool

@app.get("/api/locations")
def get_locations():
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    locations = sorted(engine.df['location_clean'].dropna().unique().tolist())
    return {"locations": locations}

@app.post("/api/recommend")
def get_recommendations(req: RecommendRequest):
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    start_time = time.time()
    trace_id = str(uuid.uuid4())
    
    telemetry_logger.log_event(trace_id, "AI_REQUEST_START", {
        "location": req.location,
        "budget_tier": req.budget,
        "cuisine": req.cuisine,
        "qualitative_input_length": len(req.qualitative) if req.qualitative else 0
    })
    
    # 1. Deterministic Filter
    candidates, widened_message = engine.filter_candidates(
        location=req.location,
        cuisine=req.cuisine,
        budget=req.budget,
        min_rating=req.min_rating
    )
    
    telemetry_logger.log_event(trace_id, "DETERMINISTIC_FILTER_COMPLETE", {
        "candidates_count": len(candidates),
        "auto_widened": bool(widened_message),
    })
    
    # 2. Call LLM Pipeline (Multi-Agent)
    results = engine.get_llm_recommendations(candidates, req, trace_id, widened_message, req.session_id)
    
    latency = time.time() - start_time
    
    telemetry_logger.log_event(trace_id, "AI_REQUEST_COMPLETE", {
        "latency_seconds": round(latency, 2),
        "source": results.get("source"),
        "candidates_filtered": len(candidates)
    })
    
    return {
        "trace_id": trace_id,
        "source": results.get("source"),
        "confidence_score": results.get("confidence_score"),
        "latency_seconds": round(latency, 2),
        "candidates_filtered": len(candidates),
        "widened_message": widened_message,
        "recommendations": results.get("recommendations", [])
    }

@app.post("/api/compare")
def compare_restaurants(req: CompareRequest):
    if not engine:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
        
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    
    result = engine.compare_candidates(req.restaurant_names, req.qualitative, trace_id)
    
    latency = time.time() - start_time
    result["latency_seconds"] = round(latency, 2)
    result["trace_id"] = trace_id
    
    return result

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    if not engine or not hasattr(engine, 'memory'):
        raise HTTPException(status_code=500, detail="MemoryManager not initialized")
    
    engine.memory.record_feedback(
        session_id=req.session_id,
        trace_id=req.trace_id,
        restaurant_name=req.restaurant_name,
        cuisine=req.cuisine,
        budget_tier=req.budget_tier,
        is_positive=req.is_positive
    )
    
    return {"status": "success"}
