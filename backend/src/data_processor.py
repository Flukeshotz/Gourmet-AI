import os
from src.config import Config
import logging

# Set HF_HOME before loading datasets
os.environ["HF_HOME"] = str(Config.DATA_DIR / "hf_cache")

import pandas as pd
from datasets import load_dataset

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_and_clean_data() -> pd.DataFrame:
    """Loads the Zomato dataset from Hugging Face and cleans/preprocesses it."""
    logging.info("Downloading/Loading Hugging Face dataset: ManikaSaini/zomato-restaurant-recommendation")
    try:
        # Load dataset
        dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation", split="train")
        df = dataset.to_pandas()
        logging.info(f"Loaded dataset with {len(df)} rows. Cleaning...")
    except Exception as e:
        logging.error(f"Failed to download from Hugging Face: {e}")
        logging.info("Generating a robust fallback Zomato mock dataset for local development...")
        # Fallback Mock Data
        mock_data = [
            {"Restaurant Name": "The Big Chill", "City": "Delhi", "Locality": "Khan Market", "Cuisines": "Italian, Continental", "Average Cost for two": 1500, "Aggregate rating": 4.5, "Votes": 2300},
            {"Restaurant Name": "Bukhara", "City": "Delhi", "Locality": "ITC Maurya", "Cuisines": "North Indian", "Average Cost for two": 5000, "Aggregate rating": 4.8, "Votes": 5400},
            {"Restaurant Name": "Truffles", "City": "Bangalore", "Locality": "Koramangala", "Cuisines": "American, Burger", "Average Cost for two": 800, "Aggregate rating": 4.6, "Votes": 8100},
            {"Restaurant Name": "Toit", "City": "Bangalore", "Locality": "Indiranagar", "Cuisines": "Continental, Italian", "Average Cost for two": 2000, "Aggregate rating": 4.7, "Votes": 9500},
            {"Restaurant Name": "Haldiram's", "City": "Delhi", "Locality": "Connaught Place", "Cuisines": "Street Food, Mithai", "Average Cost for two": 400, "Aggregate rating": 4.1, "Votes": 1200},
            {"Restaurant Name": "Nagarjuna", "City": "Bangalore", "Locality": "Residency Road", "Cuisines": "Andhra, Biryani", "Average Cost for two": 800, "Aggregate rating": 4.4, "Votes": 3200},
            {"Restaurant Name": "Oasis", "City": "Delhi", "Locality": "Vasant Kunj", "Cuisines": "Unknown", "Average Cost for two": 3000, "Aggregate rating": 3.5, "Votes": 100},
        ]
        df = pd.DataFrame(mock_data)
    
    # 1. Clean string columns
    str_cols = ['Restaurant Name', 'City', 'Locality', 'Cuisines']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Handle NaNs in Cuisines
    if 'Cuisines' in df.columns:
        df['Cuisines'] = df['Cuisines'].replace(['nan', 'NaN', 'None', ''], 'Unknown').fillna('Unknown')
    
    # Rename columns to standard app models
    rename_map = {
        'name': 'restaurant_name',
        'location': 'location',
        'cuisines': 'cuisines',
        'approx_cost(for two people)': 'average_cost',
        'rate': 'rating',
        'votes': 'votes',
        # Fallbacks for mock data
        'Restaurant Name': 'restaurant_name',
        'City': 'location',
        'Average Cost for two': 'average_cost',
        'Aggregate rating': 'rating',
        'Votes': 'votes'
    }
    df.rename(columns=rename_map, inplace=True, errors='ignore')
    
    # Fill missing rating/votes/cost
    if 'rating' in df.columns:
        # rate might be '4.1/5'
        df['rating'] = df['rating'].astype(str).str.split('/').str[0]
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
    if 'votes' in df.columns:
        df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    if 'average_cost' in df.columns:
        # average cost might have commas like '1,500'
        df['average_cost'] = df['average_cost'].astype(str).str.replace(',', '', regex=False)
        df['average_cost'] = pd.to_numeric(df['average_cost'], errors='coerce')
        # Fill missing cost with median overall to avoid crash
        median_cost = df['average_cost'].median()
        df['average_cost'] = df['average_cost'].fillna(median_cost)
        
    # Standardize Location: lowercase
    if 'location' in df.columns:
        df['location_clean'] = df['location'].str.lower()
    else:
        df['location_clean'] = "unknown"
        
    return df

def apply_budget_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates low/medium/high budget tiers per location."""
    logging.info("Calculating budget tiers per location...")
    
    def calculate_tier(group):
        low_thresh = group['average_cost'].quantile(Config.BUDGET_LOW_PERCENTILE)
        high_thresh = group['average_cost'].quantile(Config.BUDGET_HIGH_PERCENTILE)
        
        # Provide defaults if quantiles fail (e.g., all costs are the same)
        if pd.isna(low_thresh) or pd.isna(high_thresh) or low_thresh == high_thresh:
            group['budget_tier'] = 'Medium'
            return group
        
        def get_tier(cost):
            if pd.isna(cost):
                return 'Medium'
            if cost <= low_thresh:
                return 'Low'
            elif cost > high_thresh:
                return 'High'
            else:
                return 'Medium'
                
        group['budget_tier'] = group['average_cost'].apply(get_tier)
        return group
    
    # Apply calculation per location
    if 'location_clean' in df.columns:
        df = df.groupby('location_clean', group_keys=False).apply(calculate_tier)
    else:
        df = calculate_tier(df)
        
    return df

def verify_ingestion():
    logging.info("Starting ingestion pipeline...")
    df = load_and_clean_data()
    df = apply_budget_tiers(df)
    
    # Ensure columns exist
    expected_cols = ['restaurant_name', 'location', 'cuisines', 'average_cost', 'rating', 'votes', 'budget_tier']
    for col in expected_cols:
        if col not in df.columns:
            logging.warning(f"Missing expected column: {col}")
            
    # Save to parquet cache
    cache_path = Config.CACHE_FILE
    logging.info(f"Saving {len(df)} rows to cache: {cache_path}")
    df.to_parquet(cache_path, engine='pyarrow', index=False)
    logging.info("Ingestion complete.")

if __name__ == "__main__":
    verify_ingestion()
