import sys
import os
import json

# Disable OpenTelemetry to prevent connection errors to localhost:4318
# This MUST be done before importing any other packages
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = ""
os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = ""
os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = ""
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = ""
os.environ["OTEL_SERVICE_NAME"] = ""
os.environ["OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"] = "all"

# Add the parent directory to the Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the packages after OpenTelemetry is disabled
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from validator import GuardrailsPII
from guardrails import Guard
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(title="PII Detection API", version="1.0.0")

# Read configuration from environment variables
def get_entities_from_env() -> List[str]:
    """Get PII entities from environment variable or use defaults."""
    env_entities = os.getenv("PII_ENTITIES")
    if env_entities:
        try:
            return json.loads(env_entities)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in PII_ENTITIES environment variable: {env_entities}")
            print("Using default entities instead.")
    
    # Default entities if environment variable is not set or invalid
    return ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "DATE_TIME"]

def get_gpu_setting_from_env() -> bool:
    """Get GPU usage setting from environment variable or use default."""
    use_gpu_env = os.getenv("USE_GPU", "true").lower()
    return use_gpu_env in ["true", "1", "yes", "on"]

# Get configuration from environment
entities = get_entities_from_env()
use_gpu = get_gpu_setting_from_env()

print(f"Initializing GuardrailsPII with entities: {entities}")
print(f"GPU usage enabled: {use_gpu}")

# Setup Guard with PII detection using environment configuration
guard = Guard().use(
    GuardrailsPII(entities=entities, on_fail="fix", use_gpu=use_gpu)
)

class TextRequest(BaseModel):
    text: str = Field(..., description="Text to validate for PII")

class PIIEntity(BaseModel):
    piiEntity: str
    piiValue: str

class ValidationResponse(BaseModel):
    verdict: bool
    assessment: List[PIIEntity]
    anonymizedText: Optional[str] = None

class ValidationResult:
    """Class to store and format validation results."""
    def __init__(self, passed: bool, summaries: List[Dict[str, Any]], fixed_text: Optional[str] = None):
        self.passed = passed
        self.summaries = summaries
        self.fixed_text = fixed_text
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.passed,
            "assessment": self.summaries,
            "anonymized": self.fixed_text
        }

def validate_text(text: str) -> ValidationResult:
    """Validate a single text string for PII and anonymize it."""
    if not text or not isinstance(text, str):
        return ValidationResult(True, [])
    
    result = guard.validate(text)
    
    pii_entities = []
    if hasattr(result, 'validation_summaries') and result.validation_summaries:
        for summary in result.validation_summaries:
            for error in summary.error_spans:
                pii_value = text[error.start:error.end]
                pii_entities.append({
                    "piiEntity": error.reason,
                    "piiValue": pii_value
                })
    
    masked_text = result.validated_output if result.validation_passed else result.fixed_output
    return ValidationResult(result.validation_passed, pii_entities, masked_text)

@app.post("/validate", response_model=ValidationResponse)
async def validate(request: TextRequest):
    """Webhook endpoint to validate a single text field for PII."""
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Missing or empty 'text' field in request")
        
        result = validate_text(request.text)
        
        return ValidationResponse(
            verdict=result.passed,
            assessment=result.summaries,
            anonymizedText=result.fixed_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

# gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app -b 0.0.0.0:8000