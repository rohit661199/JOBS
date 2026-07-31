"""Local Ollama provider implementation supporting free offline LLMs."""
import json
from typing import Type, TypeVar
import httpx
from pydantic import BaseModel
from llm.base import BaseLLMProvider
from utils.logger import logger

T = TypeVar("T", bound=BaseModel)


class OllamaProvider(BaseLLMProvider):
    """LLM Provider interfacing with a local Ollama server."""

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.2"):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generates raw text response via Ollama generate endpoint."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "")
        except Exception as e:
            logger.error(f"Ollama connection error to {url}: {e}")
            raise

    def structured_output(self, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        """Generates JSON structured output via Ollama JSON format feature."""
        schema_json = json.dumps(schema.model_json_schema())
        augmented_prompt = (
            f"{prompt}\n\nYou MUST respond with raw JSON matching this JSON Schema:\n{schema_json}"
        )
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": augmented_prompt,
            "system": system_prompt,
            "format": "json",
            "stream": False
        }
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("response", "{}")
                parsed_json = json.loads(content)
                return schema.model_validate(parsed_json)
        except Exception as e:
            logger.error(f"Ollama structured output error: {e}")
            raise
