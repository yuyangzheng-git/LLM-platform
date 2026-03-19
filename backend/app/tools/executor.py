"""
Tool executor for executing function calls
"""
from typing import List
from .schemas import ToolCall, ToolResult
from .registry import tool_registry
import logging
import json
import traceback

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executor for tool calls"""

    @staticmethod
    async def execute_tool_call(tool_call: ToolCall) -> ToolResult:
        """
        Execute a single tool call

        Args:
            tool_call: The tool call to execute

        Returns:
            ToolResult with execution results or error
        """
        try:
            # Get tool definition
            tool_def = tool_registry.get_tool(tool_call.name)

            if not tool_def:
                error_msg = f"Tool '{tool_call.name}' not found in registry"
                logger.error(error_msg)
                return ToolResult(
                    tool_id=tool_call.id,
                    name=tool_call.name,
                    success=False,
                    error=error_msg
                )

            if not tool_def.function:
                error_msg = f"Tool '{tool_call.name}' has no function implementation"
                logger.error(error_msg)
                return ToolResult(
                    tool_id=tool_call.id,
                    name=tool_call.name,
                    success=False,
                    error=error_msg
                )

            # Execute the tool function
            logger.info(f"Executing tool '{tool_call.name}' with arguments: {tool_call.arguments}")

            result = await tool_def.function(**tool_call.arguments)

            logger.info(f"Tool '{tool_call.name}' executed successfully")

            return ToolResult(
                tool_id=tool_call.id,
                name=tool_call.name,
                success=True,
                result=result
            )

        except TypeError as e:
            error_msg = f"Invalid arguments for tool '{tool_call.name}': {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return ToolResult(
                tool_id=tool_call.id,
                name=tool_call.name,
                success=False,
                error=error_msg
            )

        except Exception as e:
            error_msg = f"Error executing tool '{tool_call.name}': {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return ToolResult(
                tool_id=tool_call.id,
                name=tool_call.name,
                success=False,
                error=error_msg
            )

    @staticmethod
    async def execute_tool_calls(tool_calls: List[ToolCall]) -> List[ToolResult]:
        """
        Execute multiple tool calls

        Args:
            tool_calls: List of tool calls to execute

        Returns:
            List of ToolResults
        """
        results = []

        for tool_call in tool_calls:
            result = await ToolExecutor.execute_tool_call(tool_call)
            results.append(result)

        return results
