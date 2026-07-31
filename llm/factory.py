"""LLM Provider factory manager."""
from config.settings import settings
from llm.base import BaseLLMProvider
from llm.gemini_provider import GeminiProvider
from llm.ollama_provider import OllamaProvider
from utils.logger import logger


def get_llm_provider(provider_type: str = None) -> BaseLLMProvider:
    """Instantiates configured LLM provider instance.

    Args:
        provider_type: 'gemini' or 'ollama'. Defaults to system setting.

    Returns:
        Instance of BaseLLMProvider.
    """
    provider_name = (provider_type or settings.llm_provider).lower()

    if provider_name == "gemini":
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY is not set in settings! Checking Ollama fallback...")
        return GeminiProvider(api_key=settings.gemini_api_key or "DUMMY_KEY")
    elif provider_name == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model_name=settings.ollama_model
        )
    else:
        raise ValueError(f"Unsupported LLM provider type: {provider_name}")
