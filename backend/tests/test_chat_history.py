"""
Chat history API for the UI: error events are typed, and reloaded messages
carry tool calls, reasoning and attachment counts.
"""
import json
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.services.llm.factory import LLMServiceFactory


class ToolThenAnswerService:
    """Asks for one tool call, then answers with reasoning."""

    def __init__(self, **kwargs):
        self.turn = 0

    def supports_tools(self):
        return True

    def get_tools_format(self):
        return "openai"

    def get_available_models(self):
        return []

    async def chat_stream(self, messages, model, temperature=0.7, max_tokens=2000, **kwargs):
        self.turn += 1
        if self.turn == 1:
            yield {
                "type": "tool_calls",
                "tool_calls": [{
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "get_current_datetime", "arguments": "{}"},
                }],
            }
        else:
            yield {"type": "content", "reasoning": "thinking it over", "content": ""}
            yield {"type": "content", "reasoning": "", "content": "final answer"}


def _sse_events(text):
    return [json.loads(line[6:]) for line in text.splitlines() if line.startswith("data: ")]


def _create_conversation(client, provider):
    resp = client.post(
        "/api/v1/conversations",
        json={"title": "t", "model_provider": provider, "model_name": "m"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_missing_model_config_sends_typed_error_event():
    with TestClient(app) as client:
        conv_id = _create_conversation(client, "gemini")
        resp = client.post("/api/v1/chat/stream", json={"conversation_id": conv_id, "message": "hi"})
    events = _sse_events(resp.text)
    assert events[0]["type"] == "error"
    assert "gemini" in events[0]["error"]


def test_history_includes_tool_calls_reasoning_and_file_count(monkeypatch):
    monkeypatch.setattr(
        LLMServiceFactory, "create_service", staticmethod(lambda **kw: ToolThenAnswerService(**kw))
    )
    with TestClient(app) as client:
        client.post(
            "/api/v1/models/configs",
            json={"provider": "anthropic", "api_key": "test-key", "enabled": True},
        )
        conv_id = _create_conversation(client, "anthropic")
        upload = client.post(
            "/api/v1/files/upload", files={"file": ("a.txt", b"hello", "text/plain")}
        )
        file_id = upload.json()["id"]

        resp = client.post(
            "/api/v1/chat/stream",
            json={"conversation_id": conv_id, "message": "what time is it", "file_ids": [file_id]},
        )
        assert resp.status_code == 200
        history = client.get(f"/api/v1/conversations/{conv_id}/messages").json()

    user, assistant = history
    assert user["fileCount"] == 1
    assert assistant["content"] == "final answer"
    assert assistant["reasoning"] == "thinking it over"
    [call] = assistant["tool_calls"]
    assert call["id"] == "call_1"
    assert call["name"] == "get_current_datetime"
    assert call["status"] == "completed"


def test_conversation_list_tolerates_null_settings():
    import asyncio
    from sqlalchemy import update
    from app.database import AsyncSessionLocal
    from app.models.conversation import Conversation

    with TestClient(app) as client:
        conv_id = _create_conversation(client, "openai")

        async def null_out():
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(Conversation)
                    .where(Conversation.id == conv_id)
                    .values(temperature=None, max_tokens=None, top_p=None)
                )
                await session.commit()

        asyncio.run(null_out())
        resp = client.get("/api/v1/conversations")
    assert resp.status_code == 200
    row = next(c for c in resp.json() if c["id"] == conv_id)
    assert row["temperature"] == 0.7
