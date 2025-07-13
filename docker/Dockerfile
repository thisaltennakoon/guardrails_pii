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
# This runs a simple cache to download models, actual configuration will be from env vars at runtime
RUN python -c "from validator import GuardrailsPII; from guardrails import Guard; print('Caching PII detection models...'); guard = Guard().use(GuardrailsPII(entities=['EMAIL_ADDRESS'], use_gpu=False)); print('Models cached successfully!')"

# Expose port 8000
EXPOSE 8000

# Start the Flask application
CMD ["python", "server.py"]
