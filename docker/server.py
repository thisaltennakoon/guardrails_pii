import sys
import os
import json
# Add the parent directory to the Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Disable OpenTelemetry to prevent connection errors to localhost:4318
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"

from flask import Flask, request, jsonify
from validator import GuardrailsPII
from guardrails import Guard
from typing import List, Dict, Any, Optional

app = Flask(__name__)

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

    # print("Validation result:", result)

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

@app.route('/validate', methods=['POST'])
def validate():
    """Webhook endpoint to validate a single text field for PII."""
    try:
        data = request.json
        if not data or "text" not in data or not data["text"]:
            return jsonify({"error": "Missing or empty 'text' field in request"}), 400

        result = validate_text(data["text"])

        return jsonify({
            "verdict": result.passed,
            "assessment": result.summaries,
            "anonymizedText": result.fixed_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
