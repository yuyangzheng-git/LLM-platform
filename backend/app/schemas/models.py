from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    model_provider: str = Field(..., pattern="^(openai|anthropic|gemini|generic)$")
    model_name: str = Field(..., min_length=1, max_length=100)
    system_prompt: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=32000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=32000)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)


class ConversationResponse(BaseModel):
    id: int
    title: str
    model_provider: str
    model_name: str
    system_prompt: Optional[str]
    temperature: float
    max_tokens: int
    top_p: float
    message_count: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    conversation_id: int
    message: str = Field(..., min_length=1)
    file_ids: Optional[List[int]] = []
    stream: bool = True


class ChatResponse(BaseModel):
    message_id: int
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class FileUploadResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_type: str
    mime_type: str
    file_size: int
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ModelConfigCreate(BaseModel):
    provider: str = Field(..., pattern="^(openai|anthropic|gemini|generic)$")
    api_key: str = Field(..., min_length=1)
    api_base_url: Optional[str] = None
    organization_id: Optional[str] = None
    default_model: Optional[str] = None
    default_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=2000, ge=1, le=32000)
    enabled: bool = True


class ModelConfigUpdate(BaseModel):
    api_key: Optional[str] = Field(None, min_length=1)
    api_base_url: Optional[str] = None
    organization_id: Optional[str] = None
    default_model: Optional[str] = None
    default_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    default_max_tokens: Optional[int] = Field(None, ge=1, le=32000)
    enabled: Optional[bool] = None


class ModelConfigResponse(BaseModel):
    id: int
    provider: str
    api_base_url: Optional[str]
    organization_id: Optional[str]
    available_models: Optional[List[str]]
    default_model: Optional[str]
    default_temperature: float
    default_max_tokens: int
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
