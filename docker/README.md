# PII Detection API Docker Setup

This directory contains the Docker configuration for the PII (Personally Identifiable Information) Detection API service. The service uses FastAPI and provides endpoints for detecting and anonymizing PII in text using machine learning models.

## 📋 Overview

The PII Detection API is built with:
- **FastAPI** for the REST API framework
- **Guardrails AI** for validation orchestration
- **Presidio** for PII detection and anonymization
- **GLiNER** (small-v2.1) for named entity recognition
- **spaCy** with English language model for NLP processing

## 🏗️ Architecture

The Dockerfile uses a multi-stage build approach:
1. **Builder Stage**: Installs build dependencies and Python packages
2. **Production Stage**: Creates a lightweight runtime environment with only necessary dependencies

## 🚀 Quick Start

### Building the Docker Image

Navigate to the project root directory and build the image:

```bash
# Build the image
docker build -f docker/Dockerfile -t pii-detection-api .

# Or with a specific tag
docker build -f docker/Dockerfile -t pii-detection-api:latest .
```

### Running the Container

#### Basic Usage

```bash
# Run with default settings
docker run -p 8000:8000 pii-detection-api
```

#### With Environment Variables

```bash
# Run with custom configuration
docker run -p 8000:8000 \
  -e WORKERS=2 \
  -e PORT=8000 \
  -e PII_ENTITIES='["PERSON","EMAIL","PHONE_NUMBER","CREDIT_CARD"]' \
  -e USE_GPU=false \
  pii-detection-api
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Port the API server listens on |
| `WORKERS` | `1` | Number of Gunicorn worker processes |
| `PII_ENTITIES` | `["PERSON","EMAIL","PHONE_NUMBER","CREDIT_CARD","SSN","DATE_TIME","LOCATION","ORGANIZATION","URL","IP_ADDRESS","IBAN_CODE","US_DRIVER_LICENSE","US_PASSPORT"]` | JSON array of PII entities to detect |
| `USE_GPU` | `false` | Enable GPU acceleration (requires CUDA-compatible setup) |

### Endpoints

#### POST /validate

Validates text for PII and returns anonymized version.

**Request Body:**
```json
{
  "text": "My name is John Doe and my email is john.doe@example.com"
}
```
