"""
End-to-end chat flow tests with a fake LLM service:
upload file -> create conversation -> chat -> answer, with and without tools.

The fake service records the `tools` kwarg it receives, which lets us verify
that enable_tools=False results in zero tool definitions being sent.
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.main import app
from app.services.llm.factory import LLMServiceFactory


class FakeLLMService:
    """In-memory LLM service that records received kwargs."""

    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.received_tools = "unset"
        FakeLLMService.instances.append(self)

    def supports_tools(self):
        return True

    def get_tools_format(self):
        return "openai"

    def get_available_models(self):
        return []

    async def chat_stream(self, messages, model, temperature=0.7, max_tokens=2000, **kwargs):
        self.received_tools = kwargs.get("tools", None)
        yield {"type": "content", "content": "streamed answer", "reasoning": ""}

    async def chat_complete(self, messages, model, temperature=0.7, max_tokens=2000, **kwargs):
        self.received_tools = kwargs.get("tools", None)
        return {
            "content": "complete answer",
            "model": model,
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }


def _fake_factory(monkeypatch):
    FakeLLMService.instances = []
    monkeypatch.setattr(
        LLMServiceFactory,
        "create_service",
        staticmethod(lambda **kwargs: FakeLLMService(**kwargs)),
    )


def _setup_conversation(client) -> int:
    """Create a model config + conversation, return conversation id."""
    resp = client.post(
        "/api/v1/models/configs",
        json={
            "provider": "openai",
            "api_key": "test-key",
            "default_model": "gpt-4o-mini",
            "enabled": True,
        },
    )
    assert resp.status_code == 201, resp.text

    resp = client.post(
        "/api/v1/conversations",
        json={
            "title": "claim verification",
            "model_provider": "openai",
            "model_name": "gpt-4o-mini",
            "temperature": 0.0,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _upload_text_file(client) -> int:
    resp = client.post(
        "/api/v1/files/upload",
        files={"file": ("claims.txt", b"The Eiffel Tower was built in 1889.\n", "text/plain")},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _collect_sse(response) -> list:
    events = []
    for line in response.iter_lines():
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: "):]))
    return events


def test_tool_enabled_stream_passes_tools_and_saves_answer(monkeypatch):
    _fake_factory(monkeypatch)
    with TestClient(app) as client:
        conversation_id = _setup_conversation(client)
        file_id = _upload_text_file(client)

        resp = client.post(
            "/api/v1/chat/stream",
            json={
                "conversation_id": conversation_id,
                "message": "Verify the claim in the file.",
                "file_ids": [file_id],
                "stream": True,
                "enable_tools": True,
            },
        )
        assert resp.status_code == 200, resp.text
        events = _collect_sse(resp)

        assert any(e.get("type") == "done" for e in events)
        assert any(e.get("type") == "chunk" and e.get("content") == "streamed answer" for e in events)

        # Tools were actually offered to the model
        assert FakeLLMService.instances[-1].received_tools not in (None, "unset")
        assert len(FakeLLMService.instances[-1].received_tools) > 0

        # The assistant answer was persisted
        resp = client.get(f"/api/v1/conversations/{conversation_id}/messages")
        assert resp.status_code == 200
        messages = resp.json()
        assert any(m["role"] == "assistant" and "streamed answer" in m["content"] for m in messages)


def test_tool_disabled_stream_sends_no_tools(monkeypatch):
    _fake_factory(monkeypatch)
    with TestClient(app) as client:
        conversation_id = _setup_conversation(client)

        resp = client.post(
            "/api/v1/chat/stream",
            json={
                "conversation_id": conversation_id,
                "message": "Verify the claim.",
                "stream": True,
                "enable_tools": False,
            },
        )
        assert resp.status_code == 200, resp.text
        _collect_sse(resp)

        # Zero tool definitions were sent when tools are disabled
        assert FakeLLMService.instances[-1].received_tools is None


def test_complete_endpoint_honors_enable_tools(monkeypatch):
    _fake_factory(monkeypatch)
    with TestClient(app) as client:
        conversation_id = _setup_conversation(client)

        resp = client.post(
            "/api/v1/chat/complete",
            json={
                "conversation_id": conversation_id,
                "message": "Hello",
                "stream": False,
                "enable_tools": False,
            },
        )
        assert resp.status_code == 200, resp.text
        assert FakeLLMService.instances[-1].received_tools is None

        resp = client.post(
            "/api/v1/chat/complete",
            json={
                "conversation_id": conversation_id,
                "message": "Hello",
                "stream": False,
                "enable_tools": True,
            },
        )
        assert resp.status_code == 200, resp.text
        assert len(FakeLLMService.instances[-1].received_tools) > 0


def test_chat_requires_conversation_id(monkeypatch):
    _fake_factory(monkeypatch)
    with TestClient(app) as client:
        resp = client.post("/api/v1/chat/stream", json={"message": "no conversation"})
        assert resp.status_code == 422  # conversation_id is required
