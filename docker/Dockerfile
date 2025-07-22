# Multi-stage optimized Dockerfile for PII Detection API
# Stage 1: Build dependencies and install packages
FROM python:3.11-slim as builder

# Set build environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Production runtime
FROM python:3.11-slim as production

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    WORKERS=1

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -g 10001 appgroup && \
    useradd -m -u 10001 -g appgroup -s /bin/bash appuser && \
    chown -R appuser:appgroup /app

# Copy application code
COPY --chown=appuser:appgroup docker/server.py .
COPY --chown=appuser:appgroup validator ./validator

# Switch to non-root user
USER 10001

# Cache the model to avoid startup delays
RUN python -c "from gliner import GLiNER; model = GLiNER.from_pretrained('urchade/gliner_small-v2.1');"

# Expose port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "gunicorn -w ${WORKERS} -k uvicorn.workers.UvicornWorker server:app -b 0.0.0.0:${PORT}"]
