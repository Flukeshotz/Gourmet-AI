import urllib.request
import ssl
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

# Bypass SSL verify if needed
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation/resolve/refs%2Fconvert%2Fparquet/default/train/0001.parquet"
out_path = Path("data/zomato_dataset_cached.parquet")

logging.info(f"Downloading {url}")
urllib.request.urlretrieve(url, out_path)
logging.info(f"Saved to {out_path}")
