"""
Tool definition schemas for function calling
"""
from typing import Dict, Any, List, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
from enum import Enum


class ToolParameterType(str, Enum):
    """Parameter type enumeration"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ToolParameter(BaseModel):
    """Tool parameter definition"""
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None
    items: Optional[Dict[str, Any]] = None  # For array types
    properties: Optional[Dict[str, Any]] = None  # For object types


class ToolDefinition(BaseModel):
    """Tool definition base class"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: List[ToolParameter] = Field(default_factory=list)
    function: Optional[Callable[..., Awaitable[Any]]] = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        properties = {}
        required = []

        for param in self.parameters:
            param_schema = {
                "type": param.type.value,
                "description": param.description
            }

            if param.enum:
                param_schema["enum"] = param.enum

            if param.items:
                param_schema["items"] = param.items

            if param.properties:
                param_schema["properties"] = param.properties

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert to Anthropic tool use format"""
        properties = {}
        required = []

        for param in self.parameters:
            param_schema = {
                "type": param.type.value,
                "description": param.description
            }

            if param.enum:
                param_schema["enum"] = param.enum

            if param.items:
                param_schema["items"] = param.items

            if param.properties:
                param_schema["properties"] = param.properties

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }


class ToolCall(BaseModel):
    """Tool call request"""
    id: str
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    """Tool execution result"""
    tool_id: str
    name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
