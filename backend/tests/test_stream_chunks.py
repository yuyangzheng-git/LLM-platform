"""
Streaming chunk handling for the OpenAI and generic OpenAI-compatible services:

- chunks with no choices (usage/metadata-only, e.g. stream_options
  include_usage) must be skipped instead of raising IndexError
- tool call deltas split across chunks must be concatenated per index
- empty-string content must not produce a content event
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio

import pytest
from openai.types.chat import ChatCompletionChunk

from app.services.llm.openai_service import OpenAIService
from app.services.llm.generic_service import GenericOpenAIService

SERVICES = [OpenAIService, GenericOpenAIService]


def make_chunk(delta=None, finish_reason=None, usage=None, no_choices=False):
    data = {
        "id": "chatcmpl-1",
        "object": "chat.completion.chunk",
        "created": 0,
        "model": "test-model",
        "choices": [] if no_choices else [
            {"index": 0, "delta": delta or {}, "finish_reason": finish_reason}
        ],
    }
    if usage is not None:
        data["usage"] = usage
    return ChatCompletionChunk.model_validate(data)


class FakeStream:
    def __init__(self, chunks):
        self._chunks = list(chunks)

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for chunk in self._chunks:
            yield chunk


def run_stream(service_cls, chunks):
    service = service_cls(api_key="test-key", base_url="http://127.0.0.1:1/v1")

    async def fake_create(**kwargs):
        return FakeStream(chunks)

    service.client.chat.completions.create = fake_create

    async def collect():
        return [event async for event in service.chat_stream(
            messages=[{"role": "user", "content": "hi"}], model="test-model"
        )]

    return asyncio.run(collect())


@pytest.mark.parametrize("service_cls", SERVICES)
def test_usage_only_chunk_is_skipped(service_cls):
    chunks = [
        make_chunk({"role": "assistant", "content": "Hel"}),
        make_chunk({"content": "lo"}),
        make_chunk({}, finish_reason="stop"),
        make_chunk(no_choices=True, usage={
            "prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5,
        }),
    ]
    events = run_stream(service_cls, chunks)
    assert [e["content"] for e in events] == ["Hel", "lo"]
    assert all(e["type"] == "content" for e in events)


@pytest.mark.parametrize("service_cls", SERVICES)
def test_leading_metadata_chunk_without_choices_is_skipped(service_cls):
    chunks = [
        make_chunk(no_choices=True),
        make_chunk({"content": "ok"}),
    ]
    events = run_stream(service_cls, chunks)
    assert [e["content"] for e in events] == ["ok"]


@pytest.mark.parametrize("service_cls", SERVICES)
def test_empty_content_does_not_emit_event(service_cls):
    chunks = [
        make_chunk({"role": "assistant", "content": ""}),
        make_chunk({"content": "x"}),
    ]
    events = run_stream(service_cls, chunks)
    assert [e["content"] for e in events] == ["x"]


@pytest.mark.parametrize("service_cls", SERVICES)
def test_tool_call_fragments_are_concatenated(service_cls):
    chunks = [
        make_chunk({"tool_calls": [{
            "index": 0, "id": "call_1", "type": "function",
            "function": {"name": "get_current_", "arguments": ""},
        }]}),
        make_chunk({"tool_calls": [{
            "index": 0, "function": {"name": "time", "arguments": '{"tz":'},
        }]}),
        make_chunk({"tool_calls": [{
            "index": 1, "id": "call_2", "type": "function",
            "function": {"name": "web_search", "arguments": '{"q":"a"}'},
        }]}),
        make_chunk({"tool_calls": [{
            "index": 0, "function": {"arguments": ' "UTC"}'},
        }]}),
        make_chunk({}, finish_reason="tool_calls"),
        make_chunk(no_choices=True, usage={
            "prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2,
        }),
    ]
    events = run_stream(service_cls, chunks)
    assert len(events) == 1
    assert events[0]["type"] == "tool_calls"
    assert events[0]["tool_calls"] == [
        {"id": "call_1", "type": "function",
         "function": {"name": "get_current_time", "arguments": '{"tz": "UTC"}'}},
        {"id": "call_2", "type": "function",
         "function": {"name": "web_search", "arguments": '{"q":"a"}'}},
    ]
