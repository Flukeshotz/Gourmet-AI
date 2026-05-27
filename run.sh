#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}  Starting Gourmet AI Application...   ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${RED}Shutting down Gourmet AI...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo -e "${GREEN}Starting FastAPI Backend...${NC}"
cd backend
source ../.venv/bin/activate
# Run backend on port 8001
uvicorn src.api:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}Starting Vite Frontend...${NC}"
cd frontend
npm run dev -- --port 5173 &
FRONTEND_PID=$!
cd ..

echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Application is running!${NC}"
echo -e "Frontend: http://localhost:5173"
echo -e "Backend:  http://localhost:8001"
echo -e "${BLUE}Press Ctrl+C to stop all services.${NC}"
echo -e "${BLUE}=======================================${NC}"

# Wait for background processes
wait
