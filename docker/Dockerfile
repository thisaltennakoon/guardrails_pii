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

# Create non-root user for security with home directory
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Set working directory
WORKDIR /app

# Set HOME environment variable for the user
ENV HOME=/home/appuser

# Copy requirements first for better Docker layer caching
COPY docker/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY docker/server.py .
COPY validator ./validator

# Cache the model to avoid startup delays
RUN python -c "from gliner import GLiNER; model = GLiNER.from_pretrained('urchade/gliner_small-v2.1');"

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Define default values using environment variables
ENV PORT=8000
ENV WORKERS=1

# Use environment variables in the command
# Note: Shell form of CMD is often needed to properly expand variables
CMD gunicorn -w ${WORKERS} -k uvicorn.workers.UvicornWorker server:app -b 0.0.0.0:${PORT}
