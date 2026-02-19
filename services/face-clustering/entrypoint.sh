#!/bin/bash
set -e

echo "=== Face Clustering Service Starting ==="

# Run batch processor (run as module so `from app import ...` resolves correctly)
echo "[1/2] Running batch processor..."
cd /app && python -m app.processor

# Start web UI
echo "[2/2] Starting web UI on port ${PORT:-7070}..."
cd /app && exec uvicorn app.server:app --host 0.0.0.0 --port "${PORT:-7070}"
