from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator
import json
import logging

from app.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.model_config import ModelConfig
from app.schemas.models import ChatRequest, ChatResponse
from app.services.llm.factory import LLMServiceFactory
from app.services.context_manager import ContextManager
from app.api.models import decrypt_api_key
from app.tools.registry import tool_registry
from app.tools.executor import ToolExecutor
from app.tools.schemas import ToolCall

logger = logging.getLogger(__name__)
router = APIRouter()


async def stream_chat_response(
    conversation: Conversation,
    user_message: str,
    file_ids: list,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Stream chat response using SSE with multi-turn tool calling support

    Yields SSE-formatted messages
    """
    try:
        # Get model configuration
        query = select(ModelConfig).where(
            ModelConfig.provider == conversation.model_provider
        )
        result = await db.execute(query)
        model_config = result.scalar_one_or_none()

        if not model_config or not model_config.enabled:
            yield f"data: {json.dumps({'error': 'Model configuration not found or disabled'})}\n\n"
            return

        # Decrypt API key
        api_key = decrypt_api_key(model_config.api_key)

        # Create LLM service
        service = LLMServiceFactory.create_service(
            provider=conversation.model_provider,
            api_key=api_key,
            api_base_url=model_config.api_base_url,
            organization_id=model_config.organization_id,
        )

        # Build context
        context_manager = ContextManager(db)
        messages = await context_manager.build_context_with_attachments(
            conversation_id=conversation.id,
            new_message=user_message,
            file_ids=file_ids,
            system_prompt=conversation.system_prompt,
            model=conversation.model_name,
        )

        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=user_message,
        )
        db.add(user_msg)
        await db.commit()
        await db.refresh(user_msg)

        # Link uploaded files to this message
        if file_ids:
            from app.models.file_attachment import FileAttachment
            for file_id in file_ids:
                file_query = select(FileAttachment).where(FileAttachment.id == file_id)
                file_result = await db.execute(file_query)
                attachment = file_result.scalar_one_or_none()
                if attachment:
                    attachment.message_id = user_msg.id
            await db.commit()

        # Get tools if service supports them
        tools = None
        if service.supports_tools():
            tools = tool_registry.get_tools_for_provider(service.get_tools_format())
            logger.info(f"Using {len(tools)} tools for provider {conversation.model_provider}")

        # Multi-turn tool calling loop
        max_iterations = 5
        iteration = 0
        full_response = ""
        reasoning_content = ""
        all_tool_calls = []  # Track all tool calls for metadata

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Tool calling iteration {iteration}/{max_iterations}")

            current_tool_calls = []

            # Stream response from LLM
            async for chunk in service.chat_stream(
                messages=messages,
                model=conversation.model_name,
                temperature=conversation.temperature,
                max_tokens=conversation.max_tokens,
                tools=tools if tools else None
            ):
                # Handle different chunk types
                if isinstance(chunk, dict):
                    chunk_type = chunk.get('type', 'content')

                    if chunk_type == 'content':
                        # Send reasoning content
                        if chunk.get('reasoning'):
                            reasoning_content += chunk['reasoning']
                            yield f"data: {json.dumps({'content': chunk['reasoning'], 'type': 'reasoning'})}\n\n"
                        # Send regular content
                        if chunk.get('content'):
                            full_response += chunk['content']
                            yield f"data: {json.dumps({'content': chunk['content'], 'type': 'chunk'})}\n\n"

                    elif chunk_type == 'tool_calls':
                        # Tool calls received
                        tool_calls = chunk.get('tool_calls', [])
                        for tool_call in tool_calls:
                            try:
                                # Parse arguments if they're strings
                                args = tool_call['function']['arguments']
                                if isinstance(args, str):
                                    args = json.loads(args)

                                tool_call_obj = ToolCall(
                                    id=tool_call['id'],
                                    name=tool_call['function']['name'],
                                    arguments=args
                                )
                                current_tool_calls.append(tool_call_obj)

                                # Send tool_call event to frontend
                                yield f"data: {json.dumps({'type': 'tool_call', 'tool_id': tool_call['id'], 'tool_name': tool_call['function']['name'], 'arguments': args})}\n\n"

                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse tool call arguments: {e}")
                                yield f"data: {json.dumps({'type': 'error', 'error': f'Invalid tool call arguments: {str(e)}'})}\n\n"

                else:
                    # Backward compatibility: plain string chunk
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk, 'type': 'chunk'})}\n\n"

            # If no tool calls, exit the loop
            if not current_tool_calls:
                logger.info("No tool calls in this iteration, exiting loop")
                break

            # Execute tool calls
            logger.info(f"Executing {len(current_tool_calls)} tool calls")
            tool_results = await ToolExecutor.execute_tool_calls(current_tool_calls)

            # Send tool results to frontend and add to messages
            for tool_result in tool_results:
                # Send tool_result event
                yield f"data: {json.dumps({'type': 'tool_result', 'tool_id': tool_result.tool_id, 'success': tool_result.success, 'result': tool_result.result, 'error': tool_result.error})}\n\n"

                # Save tool call and result for metadata
                all_tool_calls.append({
                    'call': {
                        'id': tool_result.tool_id,
                        'name': tool_result.name,
                        'arguments': next((tc.arguments for tc in current_tool_calls if tc.id == tool_result.tool_id), {})
                    },
                    'result': {
                        'success': tool_result.success,
                        'result': tool_result.result,
                        'error': tool_result.error
                    }
                })

            # Add assistant's tool calls to message history
            if conversation.model_provider == "anthropic":
                # Anthropic format
                tool_use_content = []
                for tc in current_tool_calls:
                    tool_use_content.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.arguments
                    })
                messages.append({
                    "role": "assistant",
                    "content": tool_use_content
                })

                # Add tool results as user message
                tool_result_content = []
                for tr in tool_results:
                    result_text = json.dumps(tr.result) if tr.success else tr.error
                    tool_result_content.append({
                        "type": "tool_result",
                        "tool_use_id": tr.tool_id,
                        "content": result_text
                    })
                messages.append({
                    "role": "user",
                    "content": tool_result_content
                })

            else:
                # OpenAI format
                tool_calls_openai = []
                for tc in current_tool_calls:
                    tool_calls_openai.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments)
                        }
                    })

                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls_openai
                })

                # Add tool results
                for tr in tool_results:
                    result_text = json.dumps(tr.result) if tr.success else tr.error
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tr.tool_id,
                        "name": tr.name,
                        "content": result_text
                    })

        # Get token usage (approximate for streaming)
        prompt_tokens = context_manager.estimate_token_count(
            "\n".join([str(m.get("content", "")) for m in messages]),
            conversation.model_name
        )
        completion_tokens = context_manager.estimate_token_count(
            full_response,
            conversation.model_name
        )
        total_tokens = prompt_tokens + completion_tokens

        # Save assistant message with tool call metadata
        extra_metadata = {}
        if all_tool_calls:
            extra_metadata['tool_calls'] = all_tool_calls

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            extra_metadata=extra_metadata if extra_metadata else None
        )
        db.add(assistant_msg)

        # Update conversation statistics
        conversation.message_count += 2  # user + assistant
        conversation.total_tokens += total_tokens

        await db.commit()
        await db.refresh(assistant_msg)

        # Send completion event
        yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_msg.id, 'tokens': {'prompt': prompt_tokens, 'completion': completion_tokens, 'total': total_tokens}})}\n\n"

    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream chat completion using Server-Sent Events (SSE)
    """
    # Get conversation
    query = select(Conversation).where(Conversation.id == request.conversation_id)
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Return streaming response
    return StreamingResponse(
        stream_chat_response(
            conversation=conversation,
            user_message=request.message,
            file_ids=request.file_ids or [],
            db=db
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.post("/complete", response_model=ChatResponse)
async def chat_complete(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete chat request without streaming
    """
    try:
        # Get conversation
        query = select(Conversation).where(Conversation.id == request.conversation_id)
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get model configuration
        query = select(ModelConfig).where(
            ModelConfig.provider == conversation.model_provider
        )
        result = await db.execute(query)
        model_config = result.scalar_one_or_none()

        if not model_config or not model_config.enabled:
            raise HTTPException(
                status_code=400,
                detail="Model configuration not found or disabled"
            )

        # Decrypt API key
        api_key = decrypt_api_key(model_config.api_key)

        # Create LLM service
        service = LLMServiceFactory.create_service(
            provider=conversation.model_provider,
            api_key=api_key,
            api_base_url=model_config.api_base_url,
            organization_id=model_config.organization_id,
        )

        # Build context
        context_manager = ContextManager(db)
        messages = await context_manager.build_context_with_attachments(
            conversation_id=conversation.id,
            new_message=request.message,
            file_ids=request.file_ids or [],
            system_prompt=conversation.system_prompt,
            model=conversation.model_name,
        )

        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )
        db.add(user_msg)
        await db.commit()
        await db.refresh(user_msg)

        # Link uploaded files to this message
        if request.file_ids:
            from app.models.file_attachment import FileAttachment
            for file_id in request.file_ids:
                file_query = select(FileAttachment).where(FileAttachment.id == file_id)
                file_result = await db.execute(file_query)
                attachment = file_result.scalar_one_or_none()
                if attachment:
                    attachment.message_id = user_msg.id
            await db.commit()

        # Get completion
        response = await service.chat_complete(
            messages=messages,
            model=conversation.model_name,
            temperature=conversation.temperature,
            max_tokens=conversation.max_tokens,
        )

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response["content"],
            prompt_tokens=response["usage"]["prompt_tokens"],
            completion_tokens=response["usage"]["completion_tokens"],
            total_tokens=response["usage"]["total_tokens"],
        )
        db.add(assistant_msg)

        # Update conversation statistics
        conversation.message_count += 2
        conversation.total_tokens += response["usage"]["total_tokens"]

        await db.commit()
        await db.refresh(assistant_msg)

        return ChatResponse(
            message_id=assistant_msg.id,
            content=response["content"],
            model=response["model"],
            prompt_tokens=response["usage"]["prompt_tokens"],
            completion_tokens=response["usage"]["completion_tokens"],
            total_tokens=response["usage"]["total_tokens"],
        )

    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
