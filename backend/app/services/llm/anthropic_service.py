from typing import AsyncGenerator, Dict, List, Any
from anthropic import AsyncAnthropic
from app.services.llm.base import BaseLLMService
import logging
import json

logger = logging.getLogger(__name__)


class AnthropicService(BaseLLMService):
    """Anthropic Claude API service implementation"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)

    def _format_messages(self, messages: List[Dict[str, Any]]) -> tuple:
        """
        Format messages for Anthropic API
        Anthropic requires system message to be separate
        """
        system_message = None
        formatted_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        return system_message, formatted_messages

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion from Anthropic"""
        try:
            system_message, formatted_messages = self._format_messages(messages)

            stream_params = {
                "model": model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }

            if system_message:
                stream_params["system"] = system_message

            # Add tools if provided
            if "tools" in kwargs and kwargs["tools"]:
                stream_params["tools"] = kwargs["tools"]

            async with self.client.messages.stream(**stream_params) as stream:
                tool_calls_buffer = []

                async for event in stream:
                    # Handle content block start (includes tool_use blocks)
                    if event.type == "content_block_start":
                        if hasattr(event, 'content_block') and event.content_block.type == "tool_use":
                            tool_calls_buffer.append({
                                'id': event.content_block.id,
                                'type': 'function',
                                'function': {
                                    'name': event.content_block.name,
                                    'arguments': ''
                                }
                            })

                    # Handle content block delta
                    elif event.type == "content_block_delta":
                        if hasattr(event, 'delta'):
                            # Text content
                            if event.delta.type == "text_delta":
                                yield {
                                    'type': 'content',
                                    'reasoning': '',
                                    'content': event.delta.text
                                }
                            # Tool use input delta
                            elif event.delta.type == "input_json_delta" and tool_calls_buffer:
                                tool_calls_buffer[-1]['function']['arguments'] += event.delta.partial_json

                # After stream completes, yield accumulated tool calls
                if tool_calls_buffer:
                    yield {
                        'type': 'tool_calls',
                        'tool_calls': tool_calls_buffer
                    }

        except Exception as e:
            logger.error(f"Anthropic streaming error: {str(e)}")
            raise

    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete chat request from Anthropic"""
        try:
            system_message, formatted_messages = self._format_messages(messages)

            params = {
                "model": model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if system_message:
                params["system"] = system_message

            response = await self.client.messages.create(**params)

            return {
                "content": response.content[0].text,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }
            }

        except Exception as e:
            logger.error(f"Anthropic completion error: {str(e)}")
            raise

    async def test_connection(self) -> bool:
        """Test Anthropic API connection"""
        try:
            await self.client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {str(e)}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
        ]

    def supports_tools(self) -> bool:
        """Anthropic supports tool use"""
        return True

    def get_tools_format(self) -> str:
        """Anthropic uses 'anthropic' format"""
        return "anthropic"
