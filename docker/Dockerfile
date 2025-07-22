# CPU-only Dockerfile for macOS development and Ubuntu CPU deployment
FROM python:3.11.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV USE_GPU=false
ENV PII_ENTITIES='["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "DATE_TIME"]'

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY docker/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY validator/ ./validator/
COPY docker/server.py ./server.py

# Pre-download and cache model files during build to avoid runtime delays
# Cache models for the default entities that will be used at runtime
RUN python -c "import json; import os; from validator import GuardrailsPII; from guardrails import Guard; \
entities = json.loads(os.getenv('PII_ENTITIES', '[\"EMAIL_ADDRESS\", \"PHONE_NUMBER\", \"PERSON\", \"DATE_TIME\"]')); \
use_gpu = os.getenv('USE_GPU', 'false').lower() in ['true', '1', 'yes', 'on']; \
print(f'Caching PII detection models for entities: {entities}, GPU: {use_gpu}...'); \
guard = Guard().use(GuardrailsPII(entities=entities, use_gpu=use_gpu)); \
print('Models cached successfully!')"

# Expose port 8000
EXPOSE 8000

# Create a non-root user with UID 10001 to satisfy Checkov CKV_CHOREO_1
RUN groupadd -g 10001 appgroup && useradd -m -u 10001 -g appgroup -s /bin/bash appuser

# Explicitly switch to UID 10001 instead of using "appuser"
USER 10001

# Start the Flask application
CMD ["python", "server.py"]
