"""
Tool registry for managing available tools
"""
from typing import Dict, List, Optional
from .schemas import ToolDefinition
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Singleton registry for managing tools"""

    _instance = None
    _tools: Dict[str, ToolDefinition] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register_tool(self, tool: ToolDefinition):
        """Register a tool"""
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")

        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def unregister_tool(self, name: str):
        """Unregister a tool"""
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Unregistered tool: {name}")

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name"""
        return self._tools.get(name)

    def get_all_tools(self) -> List[ToolDefinition]:
        """Get all registered tools"""
        return list(self._tools.values())

    def get_tools_for_provider(self, provider: str = "openai") -> List[Dict]:
        """Get tools formatted for a specific provider"""
        tools = []

        for tool in self._tools.values():
            if provider.lower() in ["openai", "generic"]:
                tools.append(tool.to_openai_format())
            elif provider.lower() == "anthropic":
                tools.append(tool.to_anthropic_format())
            else:
                logger.warning(f"Unknown provider: {provider}, defaulting to OpenAI format")
                tools.append(tool.to_openai_format())

        return tools

    def clear(self):
        """Clear all registered tools"""
        self._tools.clear()
        logger.info("Cleared all tools")

    def list_tool_names(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())


# Global singleton instance
tool_registry = ToolRegistry()
