"""
Tool-call loop tests for both chat endpoints (stream + complete):

- a model requesting a tool must trigger execution, a second model call with
  the tool results, and the final answer must be persisted
- enable_tools=False must never invoke the executor, even when the model
  unexpectedly returns tool calls (guarded at the execution entry)
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.main import app
from app.services.llm.factory import LLMServiceFactory
from app.tools.executor import ToolExecutor
from app.tools.schemas import ToolResult

TOOL_CALL_PAYLOAD = {
    "id": "call_1",
    "type": "function",
    "function": {"name": "get_current_time", "arguments": json.dumps({})},
}


class ScriptedLLMService:
    """LLM service that plays a scripted sequence of responses."""

    instances = []

    def __init__(self, responses=None, **kwargs):
        self.kwargs = kwargs
        self.complete_calls = 0
        self.stream_calls = 0
        self.received_tools = "unset"
        self.responses = responses or []
        ScriptedLLMService.instances.append(self)

    def supports_tools(self):
        return True

    def get_tools_format(self):
        return "openai"

    def get_available_models(self):
        return []

    async def chat_complete(self, messages, model, temperature=0.7, max_tokens=2000, **kwargs):
        self.received_tools = kwargs.get("tools", None)
        idx = min(self.complete_calls, len(self.responses) - 1)
        self.complete_calls += 1
        return self.responses[idx]

    async def chat_stream(self, messages, model, temperature=0.7, max_tokens=2000, **kwargs):
        self.received_tools = kwargs.get("tools", None)
        idx = min(self.stream_calls, len(self.responses) - 1)
        self.stream_calls += 1
        response = self.responses[idx]
        if isinstance(response, dict):
            yield response
        else:
            yield {"type": "content", "content": response, "reasoning": ""}


def _fake_factory(monkeypatch, responses):
    ScriptedLLMService.instances = []
    monkeypatch.setattr(
        LLMServiceFactory,
        "create_service",
        staticmethod(lambda **kwargs: ScriptedLLMService(responses, **kwargs)),
    )


def _spy_on_executor(monkeypatch):
    calls = {"count": 0, "tool_calls": []}

    async def fake_execute(tool_calls):
        calls["count"] += 1
        calls["tool_calls"] = list(tool_calls)
        return [
            ToolResult(tool_id=tc.id, name=tc.name, success=True, result={"time": "now"})
            for tc in tool_calls
        ]

    monkeypatch.setattr(ToolExecutor, "execute_tool_calls", staticmethod(fake_execute))
    return calls


def _setup_conversation(client) -> int:
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
            "title": "tool loop",
            "model_provider": "openai",
            "model_name": "gpt-4o-mini",
            "temperature": 0.0,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _collect_sse(response) -> list:
    events = []
    for line in response.iter_lines():
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: "):]))
    return events


def _complete_response(content, tool_calls=None):
    return {
        "content": content,
        "model": "gpt-4o-mini",
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        "tool_calls": tool_calls or [],
    }


def test_complete_executes_tools_then_returns_final_answer(monkeypatch):
    responses = [
        _complete_response(None, tool_calls=[TOOL_CALL_PAYLOAD]),
        _complete_response("The claim is verified.", tool_calls=[]),
    ]
    _fake_factory(monkeypatch, responses)
    executor = _spy_on_executor(monkeypatch)

    with TestClient(app) as client:
        conversation_id = _setup_conversation(client)

        resp = client.post(
            "/api/v1/chat/complete",
            json={
                "conversation_id": conversation_id,
                "message": "Verify the claim.",
                "stream": False,
                "enable_tools": True,
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["content"] == "The claim is verified."

        service = ScriptedLLMService.instances[-1]
        # tool call -> execute -> second model call with results
        assert executor["count"] == 1, "executor must run exactly once"
        assert executor["tool_calls"][0].name == "get_current_time"
        assert service.complete_calls == 2, "model must be called again with tool results"

        # final answer persisted
        resp = client.get(f"/api/v1/conversations/{conversation_id}/messages")
        assistant = [m for m in resp.json() if m["role"] == "assistant"]
        assert any("The claim is verified." in m["content"] for m in assistant)


def test_complete_tool_disabled_never_executes_even_if_model_returns_tools(monkeypatch):
    responses = [
        _complete_response(None, tool_calls=[TOOL_CALL_PAYLOAD]),
    ]
    _fake_factory(monkeypatch, responses)
    executor = _spy_on_executor(monkeypatch)

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
        assert executor["count"] == 0, "executor must not be invoked when tools are disabled"
        service = ScriptedLLMService.instances[-1]
        assert service.complete_calls == 1, "loop must stop without a second model call"


def test_stream_tool_disabled_never_executes_even_if_model_returns_tools(monkeypatch):
    responses = [
        {"type": "tool_calls", "tool_calls": [TOOL_CALL_PAYLOAD]},
    ]
    _fake_factory(monkeypatch, responses)
    executor = _spy_on_executor(monkeypatch)

    with TestClient(app) as client:
        conversation_id = _setup_conversation(client)

        resp = client.post(
            "/api/v1/chat/stream",
            json={
                "conversation_id": conversation_id,
                "message": "Hello",
                "stream": True,
                "enable_tools": False,
            },
        )
        assert resp.status_code == 200, resp.text
        events = _collect_sse(resp)
        assert executor["count"] == 0, "executor must not be invoked when tools are disabled"
        assert any(e.get("type") == "tool_blocked" for e in events)


def test_stream_executes_tools_when_enabled(monkeypatch):
    responses = [
        {"type": "tool_calls", "tool_calls": [TOOL_CALL_PAYLOAD]},
        {"type": "content", "content": "checked the clock", "reasoning": ""},
    ]
    _fake_factory(monkeypatch, responses)
    executor = _spy_on_executor(monkeypatch)

    with TestClient(app) as client:
        conversation_id = _setup_conversation(client)

        resp = client.post(
            "/api/v1/chat/stream",
            json={
                "conversation_id": conversation_id,
                "message": "What time is it?",
                "stream": True,
                "enable_tools": True,
            },
        )
        assert resp.status_code == 200, resp.text
        _collect_sse(resp)
        assert executor["count"] == 1
        service = ScriptedLLMService.instances[-1]
        assert service.stream_calls == 2
