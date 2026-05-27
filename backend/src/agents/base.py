import json
import logging
from typing import Dict, Any, Optional
from groq import Groq
from src.config import Config

class BaseAgent:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.client = None
        if self.api_key and self.api_key != "your_api_key_here":
            self.client = Groq(api_key=self.api_key)

    def _call_llm(self, model: str, prompt: str, temperature: float = 0.2) -> Optional[Dict[str, Any]]:
        """
        Base method to call Groq with JSON structure constraint and handle parsing.
        """
        if not self.client:
            logging.warning("Groq Client not initialized (Missing API Key).")
            return None
            
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=1024,
            )
            
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse LLM output as JSON: {e}")
                return None
        except Exception as e:
            logging.error(f"LLM API Call Error: {e}")
            return None

class AgentValidationException(Exception):
    """Raised when an agent detects an error in another agent's output."""
    def __init__(self, message, feedback_prompt):
        super().__init__(message)
        self.feedback_prompt = feedback_prompt
