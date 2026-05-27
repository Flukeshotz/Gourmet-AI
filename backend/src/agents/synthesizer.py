import logging
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent

class SynthesisTrustAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        
    def synthesize_response(self, validated_data: Dict[str, Any], widened_message: Optional[str], user_memory: Optional[str] = None) -> Dict[str, Any]:
        """
        Takes the validated output and attaches a user-friendly confidence_score
        and explanations for any widened filters.
        """
        logging.info("SynthesisTrustAgent: Formatting final output...")
        
        recs = validated_data.get("validated_recommendations", [])
        rqs = validated_data.get("rqs_score", 3)
        
        # Calculate a baseline confidence score from the Critic's RQS (1-5) -> (20-100%)
        # Adjust slightly based on whether filters had to be relaxed.
        base_confidence = rqs * 20
        if widened_message:
            base_confidence = max(10, base_confidence - 15) # Penalty for not perfectly matching strict constraints
            
        confidence_score = min(100, max(0, base_confidence))
        
        # If we had a widened message, the synthesizer could re-write it to be warmer,
        # but for performance we just attach it to the API response.
        
        return {
            "source": "LLM_Agent_Pipeline",
            "confidence_score": confidence_score,
            "widened_message": widened_message,
            "recommendations": recs
        }
