"""Abstract LLM Provider interface for unified completion and structured schema extraction."""
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM service integrations."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generates plain text response for given prompt.

        Args:
            prompt: User prompt input.
            system_prompt: Optional instructions governing model behavior.

        Returns:
            String response content.
        """
        pass

    @abstractmethod
    def structured_output(self, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        """Generates structured output parsed into Pydantic model.

        Args:
            prompt: Input text/query.
            schema: Pydantic model class defining desired output structure.
            system_prompt: Optional system prompt context.

        Returns:
            Validated instance of input Pydantic schema class.
        """
        pass
