FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source code
COPY api/ .

# Copy FeatureEngineer class from ml-pipeline (needed for feature_pipeline.pkl deserialization).
# Build context must be the repository root: docker build -f api/Dockerfile .
# In deploy/docker-compose.yml, set context: . (repo root) and dockerfile: api/Dockerfile.
COPY ml-pipeline/features.py /app/features.py

ENV MODELS_DIR=/app/models

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
