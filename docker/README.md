
```bash
# Standard Dockerfile
docker build -f docker/Dockerfile -t pii-detector .


# Run the optimized container (now starts in seconds instead of minutes!)
docker run -p 8000:8000 \
  -e PII_ENTITIES='["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "DATE_TIME"]' \
  -e USE_GPU=false \
  pii-detector
