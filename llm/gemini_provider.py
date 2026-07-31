"""Google Gemini Free API provider implementation."""
import json
from typing import Type, TypeVar
from pydantic import BaseModel
from google import genai
from google.genai import types
from llm.base import BaseLLMProvider
from utils.logger import logger

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """LLM Provider using Google Gemini client."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please set it in your environment or .env file.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generates text using Gemini model."""
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini API generation error: {e}")
            raise

    def structured_output(self, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        """Generates structured JSON mapped to Pydantic model with schema fallback."""
        schema_json = json.dumps(schema.model_json_schema())
        augmented_prompt = f"{prompt}\n\nRespond with valid JSON matching this schema:\n{schema_json}"

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                response_mime_type="application/json",
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=augmented_prompt,
                config=config,
            )
            text = response.text or "{}"
            data = json.loads(text)
            return schema.model_validate(data)
        except Exception as e:
            logger.error(f"Gemini structured output error: {e}")
            raise
