"""
Tests for the tool registry and tool registration.
Run: python -m pytest tests/ -v  (from the backend directory)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.tools.registry import ToolRegistry
from app.tools.schemas import ToolDefinition


def make_tool(name: str) -> ToolDefinition:
    return ToolDefinition(name=name, description=f"Test tool {name}")


def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = make_tool("test_tool")
    registry.register_tool(tool)
    assert registry.get_tool("test_tool") is tool
    registry.unregister_tool("test_tool")
    assert registry.get_tool("test_tool") is None


def test_get_all_tools_lists_registered():
    registry = ToolRegistry()
    registry.register_tool(make_tool("tool_a"))
    registry.register_tool(make_tool("tool_b"))
    names = {t.name for t in registry.get_all_tools()}
    assert {"tool_a", "tool_b"} <= names
    registry.unregister_tool("tool_a")
    registry.unregister_tool("tool_b")


def test_builtin_tool_registration_functions_exist():
    from app.tools import search_tool, datetime_tool, location_tool, web_scraper_tool

    for module in (search_tool, datetime_tool, location_tool, web_scraper_tool):
        register = getattr(module, "register_" + module.__name__.rsplit("_", 1)[-1] + "_tool", None)
        if register is None:
            # fall back to scanning module attributes for a register function
            register = next(
                (getattr(module, name) for name in dir(module) if name.startswith("register_")),
                None,
            )
        assert callable(register), f"{module.__name__} has no register function"
