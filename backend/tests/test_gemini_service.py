"""
GeminiService on the google-genai SDK: message conversion and request
config, with the SDK call replaced by a fake (no network, no API key).
"""
import base64
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.llm.gemini_service import GeminiService

MESSAGES = [
    {"role": "system", "content": "Be brief."},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"},
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What is this?"},
            {
                "type": "image_url",
                "image_url": {"url": "data:image/png;base64," + base64.b64encode(b"PNG").decode()},
            },
        ],
    },
]


def test_format_messages_splits_system_and_maps_roles():
    service = GeminiService(api_key="test")
    system, contents = service._format_messages(MESSAGES)
    assert system == "Be brief."
    assert [c.role for c in contents] == ["user", "model", "user"]
    last = contents[-1].parts
    assert last[0].text == "What is this?"
    assert last[1].inline_data.mime_type == "image/png"
    assert last[1].inline_data.data == b"PNG"


async def test_chat_stream_passes_config_and_yields_text(monkeypatch):
    service = GeminiService(api_key="test")
    seen = {}

    async def fake_stream(**kwargs):
        seen.update(kwargs)

        async def gen():
            for text in ("Hel", None, "lo"):
                yield SimpleNamespace(text=text)

        return gen()

    monkeypatch.setattr(service.client.aio.models, "generate_content_stream", fake_stream)
    chunks = [c async for c in service.chat_stream(MESSAGES, model="gemini-2.5-flash", temperature=0.2, max_tokens=50)]

    assert chunks == ["Hel", "lo"]
    assert seen["model"] == "gemini-2.5-flash"
    assert seen["config"].system_instruction == "Be brief."
    assert seen["config"].temperature == 0.2
    assert seen["config"].max_output_tokens == 50


async def test_chat_complete_reports_usage(monkeypatch):
    service = GeminiService(api_key="test")

    async def fake_generate(**kwargs):
        return SimpleNamespace(
            text="Hi there",
            usage_metadata=SimpleNamespace(prompt_token_count=7, candidates_token_count=3),
        )

    monkeypatch.setattr(service.client.aio.models, "generate_content", fake_generate)
    result = await service.chat_complete(MESSAGES, model="gemini-2.5-flash")
    assert result["content"] == "Hi there"
    assert result["usage"] == {"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10}
