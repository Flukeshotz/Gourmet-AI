import json
import pandas as pd
from typing import Optional, Dict, Any, List
from src.agents.base import BaseAgent
import logging

class SemanticRanker(BaseAgent):
    def __init__(self):
        super().__init__()
        
    def rank_candidates(self, model: str, candidates_df: pd.DataFrame, qualitative_preferences: Optional[str], correction_prompt: Optional[str] = None, user_memory: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Takes the deterministic candidate list and user query, and outputs a raw list of recommended restaurants with justifications.
        """
        records = candidates_df[['restaurant_name', 'location', 'cuisines', 'average_cost', 'rating', 'votes', 'budget_tier']].to_dict(orient='records')
        candidates_json = json.dumps(records, indent=2)
        
        prompt = f"""[System Persona]
You are a sophisticated local food guide and gastronomy expert. Your task is to review the candidate list of restaurants and recommend the best options matching the user's specific context.

[Context Rules]
1. ONLY recommend restaurants from the Candidate List provided below. Do not make up names.
2. Return ALL candidates provided in the Candidate List. Do not omit any restaurants. Rank them based on their alignment with the user's qualitative preferences.
3. Your explanations must highlight why they match the specific qualitative requests.
{correction_prompt if correction_prompt else ""}

{user_memory if user_memory else ""}

[User Preferences]
- Qualitative Desires: {qualitative_preferences if qualitative_preferences else "Good food"}

[Candidate List]
{candidates_json}

[Format Instructions]
Output strictly in JSON matching the following schema. Double check that every field is filled out correctly.

{{
  "raw_recommendations": [
    {{
      "restaurant_name": "<string>",
      "rank": <integer>,
      "cuisine": "<string>",
      "rating": <float>,
      "average_cost": <float>,
      "location": "<string>",
      "estimated_cost_tier": "<Low|Medium|High>",
      "justification": "<string detailing why it fits the user guidelines, noting past feedback if memory exists>",
      "highlighted_features": ["<feature1>", "<feature2>"]
    }}
  ]
}}
"""
        logging.info("SemanticRanker: Generating raw recommendations...")
        return self._call_llm(model=model, prompt=prompt)
