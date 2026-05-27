import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model Specs
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    FAST_MODEL = "llama-3.1-8b-instant"
    REASONING_MODEL = "llama-3.3-70b-versatile"
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    CACHE_FILE = DATA_DIR / "zomato_dataset_cached.parquet"
    LOGS_DIR = DATA_DIR / "logs"
    PROMPT_CACHE_FILE = DATA_DIR / "prompt_cache.json"
    
    # Thresholds & Limits
    BUDGET_LOW_PERCENTILE = 0.30
    BUDGET_HIGH_PERCENTILE = 0.80
    MAX_CANDIDATES = 15

# Ensure directories exist
Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
