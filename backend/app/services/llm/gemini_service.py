from typing import AsyncGenerator, Dict, List, Any
import google.generativeai as genai
from app.services.llm.base import BaseLLMService
import logging

logger = logging.getLogger(__name__)


class GeminiService(BaseLLMService):
    """Google Gemini API service implementation"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        genai.configure(api_key=api_key)

    def _format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format messages for Gemini API"""
        formatted = []
        for msg in messages:
            role = msg["role"]
            # Gemini uses 'model' instead of 'assistant'
            if role == "assistant":
                role = "model"
            # Skip system messages or prepend to first user message
            if role == "system":
                continue
            formatted.append({
                "role": role,
                "parts": [msg["content"]]
            })
        return formatted

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion from Gemini"""
        try:
            gemini_model = genai.GenerativeModel(model)
            formatted_messages = self._format_messages(messages)

            # Extract system message if present
            system_instruction = None
            for msg in messages:
                if msg["role"] == "system":
                    system_instruction = msg["content"]
                    break

            # Create chat session
            chat = gemini_model.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])

            # Stream response
            response = await chat.send_message_async(
                formatted_messages[-1]["parts"][0] if formatted_messages else "",
                stream=True,
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini streaming error: {str(e)}")
            raise

    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete chat request from Gemini"""
        try:
            gemini_model = genai.GenerativeModel(model)
            formatted_messages = self._format_messages(messages)

            # Create chat session
            chat = gemini_model.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])

            # Get response
            response = await chat.send_message_async(
                formatted_messages[-1]["parts"][0] if formatted_messages else ""
            )

            # Gemini doesn't provide detailed token usage
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, "usage_metadata"):
                prompt_tokens = response.usage_metadata.prompt_token_count or 0
                completion_tokens = response.usage_metadata.candidates_token_count or 0

            return {
                "content": response.text,
                "model": model,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                }
            }

        except Exception as e:
            logger.error(f"Gemini completion error: {str(e)}")
            raise

    async def test_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = await model.generate_content_async("Hi")
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-ultra",
        ]
