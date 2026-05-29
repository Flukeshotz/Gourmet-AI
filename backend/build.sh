#!/bin/bash
# Exit on error
set -o errexit

cd backend

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running data processor to cache Hugging Face dataset locally..."
python src/data_processor.py

echo "Build complete."
