from typing import AsyncGenerator, Dict, List, Any
from openai import AsyncOpenAI
from app.services.llm.base import BaseLLMService
import logging

logger = logging.getLogger(__name__)


class OpenAIService(BaseLLMService):
    """OpenAI API service implementation"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        # Support both api_base_url and base_url parameter names
        base_url = kwargs.get("api_base_url") or kwargs.get("base_url", "https://api.openai.com/v1")
        logger.info(f"Initializing OpenAI service with base_url: {base_url}")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=kwargs.get("organization_id"),
        )

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion from OpenAI"""
        try:
            # O1 models don't support temperature parameter
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }

            # Only add temperature for non-O1 models
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

                # Check for reasoning content (O1, DeepSeek reasoner models)
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
            logger.error(f"OpenAI streaming error: {str(e)}")
            raise

    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete chat request from OpenAI"""
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
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "tool_calls": tool_calls,
            }

        except Exception as e:
            logger.error(f"OpenAI completion error: {str(e)}")
            raise

    async def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            # Simple test with a minimal request
            await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4-vision-preview",
            "o1-preview",
            "o1-mini",
        ]

    def supports_tools(self) -> bool:
        """OpenAI supports function calling"""
        return True

    def get_tools_format(self) -> str:
        """OpenAI uses 'openai' format"""
        return "openai"
