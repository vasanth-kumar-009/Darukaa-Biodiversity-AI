#!/bin/bash

echo "Building scientific knowledge base..."
python rag/ingest.py

echo "Starting FastAPI server..."
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}