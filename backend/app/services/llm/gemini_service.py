from typing import AsyncGenerator, Dict, List, Any, Optional, Tuple
from google import genai
from google.genai import types
from app.services.llm.base import BaseLLMService
import base64
import logging

logger = logging.getLogger(__name__)


class GeminiService(BaseLLMService):
    """Google Gemini API service implementation (google-genai SDK)"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = genai.Client(api_key=api_key)

    @staticmethod
    def _text_of(content: Any) -> str:
        """Plain text from a string or OpenAI-style list of content parts"""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            )
        return str(content or "")

    @staticmethod
    def _parts_of(content: Any) -> List[types.Part]:
        """
        Gemini parts from a string or OpenAI-style content list. Inline
        base64 images (data: URLs) are passed through; other parts are
        reduced to their text.
        """
        if not isinstance(content, list):
            return [types.Part.from_text(text=GeminiService._text_of(content))]

        parts = []
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                parts.append(types.Part.from_text(text=part.get("text", "")))
            elif part.get("type") == "image_url":
                url = (part.get("image_url") or {}).get("url", "")
                if url.startswith("data:") and ";base64," in url:
                    header, data = url.split(",", 1)
                    mime_type = header[len("data:"):].split(";", 1)[0]
                    parts.append(
                        types.Part.from_bytes(data=base64.b64decode(data), mime_type=mime_type)
                    )
        return parts or [types.Part.from_text(text="")]

    def _format_messages(
        self, messages: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], List[types.Content]]:
        """
        Split out the system prompt and convert the rest to Gemini contents.
        Gemini uses 'model' instead of 'assistant'.
        """
        system_parts = []
        contents = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                system_parts.append(self._text_of(msg.get("content")))
                continue
            if role not in ("user", "assistant"):
                # Tool results etc. are not supported by this provider yet
                continue
            contents.append(
                types.Content(
                    role="model" if role == "assistant" else "user",
                    parts=self._parts_of(msg.get("content")),
                )
            )
        system_instruction = "\n\n".join(system_parts) if system_parts else None
        return system_instruction, contents

    def _config(
        self, system_instruction: Optional[str], temperature: float, max_tokens: int
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

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
            system_instruction, contents = self._format_messages(messages)
            stream = await self.client.aio.models.generate_content_stream(
                model=model,
                contents=contents,
                config=self._config(system_instruction, temperature, max_tokens),
            )
            async for chunk in stream:
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
            system_instruction, contents = self._format_messages(messages)
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=self._config(system_instruction, temperature, max_tokens),
            )

            prompt_tokens = 0
            completion_tokens = 0
            usage = response.usage_metadata
            if usage is not None:
                prompt_tokens = usage.prompt_token_count or 0
                completion_tokens = usage.candidates_token_count or 0

            return {
                "content": response.text or "",
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
        """Test Gemini API connection (lists models; no tokens generated)"""
        try:
            await self.client.aio.models.list(config={"page_size": 1})
            return True
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
        return [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ]
