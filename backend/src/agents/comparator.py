import json
from typing import Dict, Any, List
from src.agents.base import BaseAgent
import logging

class ComparisonAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        
    def generate_comparison(self, model: str, selected_restaurants: List[Dict], qualitative_preferences: str) -> Dict[str, Any]:
        """
        Takes a list of selected restaurants and generates a comparative analysis.
        """
        restaurants_json = json.dumps(selected_restaurants, indent=2)
        
        prompt = f"""[System Persona]
You are an expert culinary advisor helping a user choose between a few selected restaurants.

[User's Goal/Preferences]
{qualitative_preferences if qualitative_preferences else "Looking for a great dining experience."}

[Selected Restaurants]
{restaurants_json}

[Task]
Analyze the selected restaurants side-by-side in the context of the user's specific goals. Provide a pros/cons matrix for each, and a final verdict on which one they should choose and why.

[Format Instructions]
Output strictly in JSON matching the following schema:
{{
  "comparisons": [
    {{
      "restaurant_name": "<string>",
      "pros": ["<pro1>", "<pro2>"],
      "cons": ["<con1>", "<con2>"],
      "fit_score": <int 1-10>
    }}
  ],
  "verdict": "<string explaining the final recommendation between these options>"
}}
"""
        logging.info("ComparisonAgent: Generating side-by-side comparison...")
        result = self._call_llm(model=model, prompt=prompt, temperature=0.3)
        if not result:
            return {
                "comparisons": [],
                "verdict": "Unable to generate comparison at this time."
            }
        return result
