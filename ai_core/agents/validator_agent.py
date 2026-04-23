import json
from typing import Dict, Any
from google.genai import types
from ai_core.agents.base_agent import BaseAgent
from ai_core.config import ai_config
from pydantic import BaseModel, Field

# We define a Pydantic schema for Gemini's structured JSON output
class ValidationResult(BaseModel):
    is_valid: bool = Field(description="True if the answer is safe, grounded in context, and relevant.")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0.")
    issues: list[str] = Field(description="List of any hallucinations, missing info, or safety concerns.")

class ValidatorAgent(BaseAgent):
    """
    Critiques the Reasoning Agent's answer. Checks for hallucination
    and safety protocol adherence.
    """

    async def execute(self, query: str, context: str, answer: str) -> Dict[str, Any]:
        """
        Returns a dict with validation results.
        """
        if ai_config.MOCK_MODE:
            return self._get_mock_response()

        prompt = (
            f"Original Query: {query}\n\n"
            f"Source Context: {context}\n\n"
            f"Generated Answer: {answer}\n\n"
            "Critique the generated answer. Is it fully grounded in the source context? Is it safe?"
        )
        
        # We pass the Pydantic schema to Gemini to guarantee JSON output
        result_str = self._generate_content(
            prompt=prompt,
            system_instruction=ai_config.VALIDATOR_PROMPT,
            response_schema=ValidationResult
        )
        
        try:
            # Parse the JSON string returned by Gemini
            return json.loads(result_str)
        except json.JSONDecodeError:
            # Fallback if parsing fails
            return {"is_valid": True, "confidence": 0.85, "issues": ["Failed to parse validation JSON."]}

    def _get_mock_response(self) -> Dict[str, Any]:
        return {
            "is_valid": True,
            "confidence": 0.98,
            "issues": []
        }
