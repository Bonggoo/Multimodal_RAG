#!/bin/bash
# Script to start the FastAPI server locally using Poetry

echo "Starting Multimodal RAG API Server..."
echo "Host: 0.0.0.0"
echo "Port: 8000"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create one from .env.example"
    exit 1
fi

# Run server
poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
