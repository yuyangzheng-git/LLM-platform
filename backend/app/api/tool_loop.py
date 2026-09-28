"""
Shared tool-call loop logic for the streaming and non-streaming chat endpoints.

Both endpoints go through the same functions so the execution rules are
identical: tool calls are executed only when enable_tools is True (checked
again at the execution entry as defense in depth — models can emit tool
calls even when no tools were sent), and results are appended to the message
history in the provider's format before the next model call.
"""
import json
import logging
from typing import Any, Dict, List, Tuple

from app.tools.executor import ToolExecutor
from app.tools.schemas import ToolCall

logger = logging.getLogger(__name__)


def parse_tool_calls(raw_tool_calls: List[Dict[str, Any]]) -> List[ToolCall]:
    """Convert provider tool-call dicts (openai-style) into ToolCall objects."""
    parsed: List[ToolCall] = []
    for tc in raw_tool_calls or []:
        try:
            args = tc["function"]["arguments"]
            if isinstance(args, str):
                args = json.loads(args)
            parsed.append(
                ToolCall(
                    id=tc["id"],
                    name=tc["function"]["name"],
                    arguments=args,
                )
            )
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse tool call {tc}: {e}")
    return parsed


async def execute_guarded(
    tool_calls: List[ToolCall],
    enable_tools: bool,
) -> Tuple[List[Any], bool]:
    """
    Execute tool calls only when tools are enabled.

    Returns (results, executed). When enable_tools is False the executor is
    NOT invoked at all — this guards against providers that return tool
    calls even though no tool definitions were sent.
    """
    if not enable_tools:
        logger.warning(
            f"Model returned {len(tool_calls)} tool call(s) but enable_tools=False; "
            "skipping execution"
        )
        return [], False
    return await ToolExecutor.execute_tool_calls(tool_calls), True


def append_tool_messages(
    messages: List[Dict[str, Any]],
    tool_calls: List[ToolCall],
    tool_results: List[Any],
    model_provider: str,
) -> None:
    """Append assistant tool-call + tool-result messages (provider format)."""
    if model_provider == "anthropic":
        messages.append({
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.arguments}
                for tc in tool_calls
            ],
        })
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tr.tool_id,
                    "content": json.dumps(tr.result) if tr.success else tr.error,
                }
                for tr in tool_results
            ],
        })
    else:
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                }
                for tc in tool_calls
            ],
        })
        for tr in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tr.tool_id,
                "name": tr.name,
                "content": json.dumps(tr.result) if tr.success else tr.error,
            })
