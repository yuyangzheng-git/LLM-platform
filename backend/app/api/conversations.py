from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from typing import List

from app.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.file_attachment import FileAttachment
from app.schemas.models import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse
)

router = APIRouter()


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    conversation = Conversation(
        title=conversation_data.title,
        model_provider=conversation_data.model_provider,
        model_name=conversation_data.model_name,
        system_prompt=conversation_data.system_prompt,
        temperature=conversation_data.temperature,
        max_tokens=conversation_data.max_tokens,
        top_p=conversation_data.top_p,
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return conversation


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations with pagination"""
    query = select(Conversation).order_by(
        Conversation.updated_at.desc()
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    conversations = result.scalars().all()

    return conversations


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation by ID"""
    query = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a conversation"""
    query = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Update fields
    update_data = conversation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)

    await db.commit()
    await db.refresh(conversation)

    return conversation


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    query = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()

    return None


@router.get("/{conversation_id}/messages", response_model=List[dict])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a conversation"""
    # Verify conversation exists
    query = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).offset(skip).limit(limit)

    result = await db.execute(query)
    messages = result.scalars().all()

    # Attachment counts per message, so the UI can show "N files attached"
    file_counts = {}
    message_ids = [msg.id for msg in messages]
    if message_ids:
        count_query = (
            select(FileAttachment.message_id, func.count(FileAttachment.id))
            .where(FileAttachment.message_id.in_(message_ids))
            .group_by(FileAttachment.message_id)
        )
        file_counts = dict((await db.execute(count_query)).all())

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "prompt_tokens": msg.prompt_tokens,
            "completion_tokens": msg.completion_tokens,
            "total_tokens": msg.total_tokens,
            "created_at": msg.created_at,
            "fileCount": file_counts.get(msg.id, 0),
            **_metadata_for_ui(msg.extra_metadata),
        }
        for msg in messages
    ]


def _metadata_for_ui(metadata) -> dict:
    """
    Tool calls and reasoning saved on an assistant message, reshaped to the
    same form the frontend builds from live stream events.
    """
    if not metadata:
        return {}
    out = {}
    if metadata.get("reasoning"):
        out["reasoning"] = metadata["reasoning"]
    tool_calls = []
    for entry in metadata.get("tool_calls") or []:
        call = entry.get("call", {})
        result = entry.get("result", {})
        tool_calls.append({
            "id": call.get("id"),
            "name": call.get("name"),
            "arguments": call.get("arguments", {}),
            "status": "completed" if result.get("success") else "error",
            "result": result.get("result"),
            "error": result.get("error"),
        })
    if tool_calls:
        out["tool_calls"] = tool_calls
    return out
