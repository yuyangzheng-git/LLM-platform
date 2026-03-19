from typing import Dict, Any
from app.services.llm.base import BaseLLMService
from app.services.llm.openai_service import OpenAIService
from app.services.llm.anthropic_service import AnthropicService
from app.services.llm.gemini_service import GeminiService
from app.services.llm.generic_service import GenericOpenAIService
import logging

logger = logging.getLogger(__name__)


class LLMServiceFactory:
    """Factory class to create LLM service instances"""

    _service_map = {
        "openai": OpenAIService,
        "anthropic": AnthropicService,
        "gemini": GeminiService,
        "generic": GenericOpenAIService,
    }

    @classmethod
    def create_service(
        cls,
        provider: str,
        api_key: str,
        **kwargs
    ) -> BaseLLMService:
        """
        Create an LLM service instance

        Args:
            provider: Provider name (openai, anthropic, gemini, generic)
            api_key: API key for the provider
            **kwargs: Additional configuration (api_base_url, organization_id, etc.)

        Returns:
            BaseLLMService instance

        Raises:
            ValueError: If provider is not supported
        """
        service_class = cls._service_map.get(provider.lower())

        if not service_class:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {', '.join(cls._service_map.keys())}"
            )

        logger.info(f"Creating {provider} service")
        return service_class(api_key=api_key, **kwargs)

    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported providers"""
        return list(cls._service_map.keys())
