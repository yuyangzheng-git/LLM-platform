from typing import AsyncGenerator, Dict, List, Any
from openai import AsyncOpenAI
from app.services.llm.base import BaseLLMService
import logging

logger = logging.getLogger(__name__)


class GenericOpenAIService(BaseLLMService):
    """Generic OpenAI-compatible API service (e.g., local models, other providers)"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        base_url = kwargs.get("api_base_url", "http://localhost:8000/v1")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.base_url = base_url

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion from generic OpenAI-compatible API"""
        try:
            # Some models (like DeepSeek) might not support temperature or other params
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }

            # Add temperature if model supports it
            if not model.startswith('o1'):
                params["temperature"] = temperature

            stream = await self.client.chat.completions.create(**params)

            # Buffer for accumulating tool calls
            tool_calls_buffer = {}

            async for chunk in stream:
                delta = chunk.choices[0].delta

                # Handle tool calls
                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        idx = tool_call_delta.index

                        # Initialize buffer for this tool call
                        if idx not in tool_calls_buffer:
                            tool_calls_buffer[idx] = {
                                'id': '',
                                'type': 'function',
                                'function': {
                                    'name': '',
                                    'arguments': ''
                                }
                            }

                        # Accumulate tool call data
                        if tool_call_delta.id:
                            tool_calls_buffer[idx]['id'] = tool_call_delta.id

                        if tool_call_delta.function:
                            if tool_call_delta.function.name:
                                tool_calls_buffer[idx]['function']['name'] += tool_call_delta.function.name
                            if tool_call_delta.function.arguments:
                                tool_calls_buffer[idx]['function']['arguments'] += tool_call_delta.function.arguments

                # Check for reasoning content (DeepSeek reasoner, O1-like models)
                has_reasoning = hasattr(delta, 'reasoning_content') and delta.reasoning_content
                has_content = delta.content

                if has_reasoning or has_content:
                    yield {
                        'type': 'content',
                        'reasoning': delta.reasoning_content if has_reasoning else '',
                        'content': delta.content if has_content else ''
                    }

            # After stream completes, yield accumulated tool calls
            if tool_calls_buffer:
                yield {
                    'type': 'tool_calls',
                    'tool_calls': list(tool_calls_buffer.values())
                }

        except Exception as e:
            logger.error(f"Generic OpenAI streaming error: {str(e)}")
            raise

    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete chat request from generic OpenAI-compatible API"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs
            )

            message = response.choices[0].message
            tool_calls = []
            if getattr(message, "tool_calls", None):
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "type": getattr(tc, "type", "function"),
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments or "",
                        },
                    })

            return {
                "content": message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                "tool_calls": tool_calls,
            }

        except Exception as e:
            logger.error(f"Generic OpenAI completion error: {str(e)}")
            raise

    async def test_connection(self) -> bool:
        """Test generic API connection"""
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Generic OpenAI connection test failed: {str(e)}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available models from generic API"""
        # For generic APIs, this should be fetched from the API
        # Returning empty list as placeholder
        return []

    def supports_tools(self) -> bool:
        """Generic OpenAI-compatible APIs support function calling"""
        return True

    def get_tools_format(self) -> str:
        """Generic APIs use 'openai' format"""
        return "openai"
