import logging
from typing import Any, Dict
from google import genai
from google.genai import types
from ai_core.config import ai_config

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Abstract base class for all AI agents in the pipeline.
    Provides shared access to the Gemini client and trace recording.
    """

    def __init__(self):
        # We only initialize the client if we're not in mock mode,
        # or we initialize it lazily when needed.
        self._client = None
        
    @property
    def client(self) -> genai.Client:
        """Lazy load the Gemini client so it doesn't fail on startup if API key is missing."""
        if self._client is None and not ai_config.MOCK_MODE:
            self._client = genai.Client(api_key=ai_config.GEMINI_API_KEY)
        return self._client

    async def execute(self, **kwargs) -> Any:
        """
        Main execution method for the agent. Must be implemented by subclasses.
        """
        raise NotImplementedError("Agents must implement the execute() method.")

    def _generate_content(self, prompt: str, system_instruction: str = None, response_schema=None) -> str:
        """
        Helper method to call Gemini, handling mock mode automatically.
        """
        if ai_config.MOCK_MODE:
            logger.info(f"[{self.__class__.__name__}] Executing in MOCK MODE.")
            return self._get_mock_response()

        # Build config
        config_kwargs = {
            "temperature": ai_config.GEMINI_TEMPERATURE,
            "max_output_tokens": ai_config.GEMINI_MAX_TOKENS,
        }
        
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
            
        if response_schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_schema
            
        config = types.GenerateContentConfig(**config_kwargs)

        try:
            response = self.client.models.generate_content(
                model=ai_config.GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            raise e

    def _get_mock_response(self) -> str:
        """Override this in subclasses to provide specific mock data."""
        return "This is a mock response from the agent."
