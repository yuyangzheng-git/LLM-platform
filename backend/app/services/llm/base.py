from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Any, Optional


class BaseLLMService(ABC):
    """Abstract base class for LLM services"""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion responses

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name/identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Text chunks from the streaming response
        """
        pass

    @abstractmethod
    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete chat request without streaming

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name/identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary with 'content', 'model', 'usage' (prompt_tokens, completion_tokens, total_tokens)
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the API connection is valid"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass

    def supports_tools(self) -> bool:
        """
        Check if this provider supports function calling/tools

        Returns:
            True if the provider supports tools, False otherwise
        """
        return False

    def get_tools_format(self) -> str:
        """
        Get the tools format used by this provider

        Returns:
            'openai' or 'anthropic'
        """
        return "openai"
