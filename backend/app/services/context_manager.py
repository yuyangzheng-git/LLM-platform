from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.file_attachment import FileAttachment
from app.services.file_handler import FileHandler
import logging
import tiktoken
import os

logger = logging.getLogger(__name__)

# Models that support vision/multimodal input
VISION_CAPABLE_MODELS = {
    # OpenAI
    'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4-vision-preview',
    'gpt-5', 'gpt-5.1', 'gpt-5.2', 'gpt-5.2-pro', 'gpt-5.3', 'gpt-5.4', 'gpt-5.4-pro',
    'gpt-4.1', 'gpt-4.5-preview',

    # Claude (all Claude 3+ models support vision)
    'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku', 'claude-3-5-sonnet',
    'claude-3-7-sonnet', 'claude-opus-4', 'claude-sonnet-4', 'claude-haiku-4',
    'claude-opus-4-1', 'claude-opus-4-5', 'claude-opus-4-6',
    'claude-sonnet-4-5', 'claude-sonnet-4-6', 'claude-haiku-4-5',

    # Gemini (all Gemini 1.5+ support vision)
    'gemini-pro-vision', 'gemini-1.5-pro', 'gemini-1.5-flash',
    'gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-pro',
    'gemini-3-pro', 'gemini-3-flash', 'gemini-3.1-pro',

    # Grok
    'grok-vision', 'grok-2-vision', 'grok-3', 'grok-4', 'grok-4.1',

    # Qwen VL
    'qwen-vl', 'qwen2-vl', 'qwen2.5-vl', 'qwen3-vl',
    'qvq-max', 'qvq-plus'
}

def is_vision_capable(model: str) -> bool:
    """Check if model supports vision/multimodal input"""
    model_lower = model.lower()
    return any(capable_model in model_lower for capable_model in VISION_CAPABLE_MODELS)


class ContextManager:
    """Manager for conversation context and history"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def load_conversation_history(
        self,
        conversation_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load conversation message history

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to load (most recent)

        Returns:
            List of message dictionaries with role and content
        """
        try:
            query = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc())

            if limit:
                # Get most recent N messages
                query = query.limit(limit)

            result = await self.db.execute(query)
            messages = result.scalars().all()

            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "message_id": msg.id,
                }
                for msg in messages
            ]

        except Exception as e:
            logger.error(f"Load conversation history error: {str(e)}")
            return []

    async def load_message_attachments(
        self,
        message_id: int
    ) -> List[FileAttachment]:
        """
        Load file attachments for a message

        Args:
            message_id: Message ID

        Returns:
            List of FileAttachment objects
        """
        try:
            query = select(FileAttachment).where(
                FileAttachment.message_id == message_id
            )
            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Load message attachments error: {str(e)}")
            return []

    async def build_context_with_attachments(
        self,
        conversation_id: int,
        new_message: str,
        file_ids: Optional[List[int]] = None,
        system_prompt: Optional[str] = None,
        message_limit: Optional[int] = None,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Build complete conversation context including attachments

        Args:
            conversation_id: Conversation ID
            new_message: New user message
            file_ids: List of file attachment IDs for new message
            system_prompt: System prompt to prepend
            message_limit: Limit on history messages
            model: Model name to determine vision capability

        Returns:
            List of formatted messages for LLM
        """
        messages = []
        vision_capable = is_vision_capable(model) if model else False

        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Load conversation history
        history = await self.load_conversation_history(conversation_id, message_limit)

        # Process history messages and their attachments
        for msg in history:
            content = msg["content"]
            attachments = await self.load_message_attachments(msg["message_id"])

            if attachments:
                if vision_capable:
                    # Use multimodal format for vision-capable models
                    content_parts = [{"type": "text", "text": content}]

                    for attachment in attachments:
                        if attachment.file_type == "image":
                            # Get image base64
                            image_data = await FileHandler.get_file_content(
                                attachment.file_path,
                                attachment.file_type
                            )
                            if image_data:
                                # Get mime type from file extension
                                ext = os.path.splitext(attachment.original_filename)[1].lower()
                                mime_type = {
                                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                                    '.png': 'image/png', '.gif': 'image/gif',
                                    '.webp': 'image/webp'
                                }.get(ext, 'image/jpeg')

                                content_parts.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{image_data}"
                                    }
                                })
                        elif attachment.processed_content:
                            # Text-based attachments
                            content_parts[0]["text"] += f"\n\n[File: {attachment.original_filename}]\n{attachment.processed_content}"

                    messages.append({
                        "role": msg["role"],
                        "content": content_parts
                    })
                else:
                    # Text-only format for non-vision models
                    attachment_texts = []
                    for attachment in attachments:
                        if attachment.processed_content:
                            attachment_texts.append(
                                f"[File: {attachment.original_filename}]\n{attachment.processed_content}"
                            )
                        elif attachment.file_type == "image":
                            attachment_texts.append(
                                f"[Image: {attachment.original_filename}] (图片内容无法显示，此模型不支持视觉)"
                            )

                    if attachment_texts:
                        content = content + "\n\n" + "\n\n".join(attachment_texts)

                    messages.append({
                        "role": msg["role"],
                        "content": content
                    })
            else:
                messages.append({
                    "role": msg["role"],
                    "content": content
                })

        # Build new user message with attachments
        if file_ids:
            if vision_capable:
                # Multimodal format
                content_parts = [{"type": "text", "text": new_message}]

                for file_id in file_ids:
                    query = select(FileAttachment).where(FileAttachment.id == file_id)
                    result = await self.db.execute(query)
                    attachment = result.scalar_one_or_none()

                    if attachment:
                        if attachment.file_type == "image":
                            image_data = await FileHandler.get_file_content(
                                attachment.file_path,
                                attachment.file_type
                            )
                            if image_data:
                                ext = os.path.splitext(attachment.original_filename)[1].lower()
                                mime_type = {
                                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                                    '.png': 'image/png', '.gif': 'image/gif',
                                    '.webp': 'image/webp'
                                }.get(ext, 'image/jpeg')

                                content_parts.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{image_data}"
                                    }
                                })
                        elif attachment.processed_content:
                            content_parts[0]["text"] += f"\n\n[File: {attachment.original_filename}]\n{attachment.processed_content}"

                messages.append({
                    "role": "user",
                    "content": content_parts
                })
            else:
                # Text-only format
                attachment_texts = []
                for file_id in file_ids:
                    query = select(FileAttachment).where(FileAttachment.id == file_id)
                    result = await self.db.execute(query)
                    attachment = result.scalar_one_or_none()

                    if attachment:
                        if attachment.processed_content:
                            attachment_texts.append(
                                f"[File: {attachment.original_filename}]\n{attachment.processed_content}"
                            )
                        elif attachment.file_type == "image":
                            attachment_texts.append(
                                f"[Image: {attachment.original_filename}] (图片内容无法显示，此模型不支持视觉)"
                            )

                new_content = new_message
                if attachment_texts:
                    new_content = new_message + "\n\n" + "\n\n".join(attachment_texts)

                messages.append({
                    "role": "user",
                    "content": new_content
                })
        else:
            # No attachments
            messages.append({
                "role": "user",
                "content": new_message
            })

        return messages

    @staticmethod
    def estimate_token_count(text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Estimate token count for text

        Args:
            text: Text to count tokens for
            model: Model name for tokenizer

        Returns:
            Estimated token count
        """
        try:
            # Try to get encoding for model
            try:
                encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fall back to cl100k_base encoding
                encoding = tiktoken.get_encoding("cl100k_base")

            return len(encoding.encode(text))

        except Exception as e:
            logger.warning(f"Token estimation error: {str(e)}, using approximate count")
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4

    async def get_conversation_token_count(
        self,
        conversation_id: int
    ) -> int:
        """
        Get total token count for conversation

        Args:
            conversation_id: Conversation ID

        Returns:
            Total token count
        """
        try:
            query = select(Conversation).where(Conversation.id == conversation_id)
            result = await self.db.execute(query)
            conversation = result.scalar_one_or_none()

            if conversation:
                return conversation.total_tokens

            return 0

        except Exception as e:
            logger.error(f"Get token count error: {str(e)}")
            return 0
