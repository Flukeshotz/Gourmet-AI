import json
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
from src.config import Config

class PromptCache:
    def __init__(self, cache_file: Path = Config.PROMPT_CACHE_FILE):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
        
    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            import logging
            logging.error(f"Failed to save prompt cache: {e}")

    def generate_hash(self, location: str, cuisine: Optional[str], budget: Optional[str], min_rating: float, qualitative: Optional[str]) -> str:
        """
        Generates a SHA-256 hash for the given parameters to use as a cache key.
        """
        key_string = f"{location.lower().strip()}_{str(cuisine).lower().strip()}_{str(budget).lower().strip()}_{min_rating}_{str(qualitative).lower().strip()}"
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

    def get(self, hash_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the cached JSON response if it exists.
        """
        return self.cache.get(hash_key)
        
    def set(self, hash_key: str, data: Dict[str, Any]):
        """
        Stores the JSON response in the cache and persists to disk.
        """
        self.cache[hash_key] = data
        self._save_cache()

# Global singleton
prompt_cache = PromptCache()
