### Build and Run (CPU-only)

```bash
# Build CPU-only image (works on macOS)
docker build -f docker/Dockerfile -t pii-detector:latest .

# Run without GPU
docker run -p 8000:8000 \
  -e USE_GPU=false \
  -e PII_ENTITIES='["EMAIL_ADDRESS", "PHONE_NUMBER"]' \
  pii-detector:latest

# Or use docker-compose
docker-compose up pii-detector-cpu
```

## Production Deployment on Ubuntu

### Build and Run (with GPU support)

```bash
# Build GPU-enabled image (Ubuntu/Linux only)
docker build -f docker/Dockerfile.gpu -t pii-detector-gpu:latest .

# Run with GPU support
docker run --gpus all -p 8000:8000 \
  -e USE_GPU=true \
  -e PII_ENTITIES='["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "DATE_TIME"]' \
  pii-detector-gpu:latest