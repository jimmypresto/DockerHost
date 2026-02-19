FROM python:3.11-slim

# System deps for OpenCV + libgomp (OpenMP for InsightFace)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    g++ \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# InsightFace will cache models here (volume mounted at runtime too)
ENV INSIGHTFACE_HOME=/app/models

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download buffalo_l model at build time to avoid CDN dependency at runtime
COPY download_models.py .
RUN python download_models.py

COPY app/ ./app/

# entrypoint: run processor then start web server
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
