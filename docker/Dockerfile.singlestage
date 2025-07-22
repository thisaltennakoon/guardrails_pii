# Use Python 3.11 slim image for smaller footprint
FROM python:3.11-slim

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for the packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY docker/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY docker/server.py .
COPY validator ./validator

# Create a non-root user with UID 10001 to satisfy Checkov CKV_CHOREO_1
RUN groupadd -g 10001 appgroup && useradd -m -u 10001 -g appgroup -s /bin/bash appuser

# Explicitly switch to UID 10001 instead of using "appuser"
USER 10001

# Cache the model to avoid startup delays
RUN python -c "from gliner import GLiNER; model = GLiNER.from_pretrained('urchade/gliner_small-v2.1');"

# Expose the port
EXPOSE 8000

# Define default values using environment variables
ENV PORT=8000
ENV WORKERS=1

CMD gunicorn -w ${WORKERS} -k uvicorn.workers.UvicornWorker server:app -b 0.0.0.0:${PORT}
