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
from app.api.tool_loop import parse_tool_calls, execute_guarded, append_tool_messages

logger = logging.getLogger(__name__)
router = APIRouter()

# Shown to clients instead of raw exception text; details go to the server log.
PUBLIC_ERROR_MESSAGE = "生成回复时出错，请稍后重试或检查服务器日志"
MODEL_NOT_CONFIGURED_MESSAGE = "模型服务（{provider}）尚未配置或已停用，请先在服务器上完成模型配置"


async def stream_chat_response(
    conversation: Conversation,
    user_message: str,
    file_ids: list,
    db: AsyncSession,
    enable_tools: bool = True
) -> AsyncGenerator[str, None]:
    """
    Stream chat response using SSE with multi-turn tool calling support

    When enable_tools is False, no tool definitions are sent to the model and
    the tool-execution loop is skipped entirely (used for tool-free control
    conditions in experiments).

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
            yield f"data: {json.dumps({'type': 'error', 'error': MODEL_NOT_CONFIGURED_MESSAGE.format(provider=conversation.model_provider)})}\n\n"
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

        # Get tools if service supports them (disabled in tool-free conditions)
        tools = None
        if enable_tools and service.supports_tools():
            tools = tool_registry.get_tools_for_provider(service.get_tools_format())
            logger.info(f"Using {len(tools)} tools for provider {conversation.model_provider}")
        elif not enable_tools:
            logger.info(f"Tools disabled for this request (enable_tools=False)")

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
            stream_kwargs = {}
            if tools:
                stream_kwargs["tools"] = tools
            async for chunk in service.chat_stream(
                messages=messages,
                model=conversation.model_name,
                temperature=conversation.temperature,
                max_tokens=conversation.max_tokens,
                **stream_kwargs
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
                        for tool_call in parse_tool_calls(tool_calls):
                            current_tool_calls.append(tool_call)
                            # Send tool_call event to frontend
                            yield f"data: {json.dumps({'type': 'tool_call', 'tool_id': tool_call.id, 'tool_name': tool_call.name, 'arguments': tool_call.arguments})}\n\n"

                else:
                    # Backward compatibility: plain string chunk
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk, 'type': 'chunk'})}\n\n"

            # If no tool calls, exit the loop
            if not current_tool_calls:
                logger.info("No tool calls in this iteration, exiting loop")
                break

            # Execute tool calls only when tools are enabled (guarded again at
            # the execution entry: a model may emit tool calls even though no
            # tool definitions were sent when enable_tools=False)
            logger.info(f"Executing {len(current_tool_calls)} tool calls")
            tool_results, executed = await execute_guarded(current_tool_calls, enable_tools)

            if not executed:
                yield f"data: {json.dumps({'type': 'tool_blocked', 'count': len(current_tool_calls), 'message': 'Tool execution disabled (enable_tools=False)'})}\n\n"
                break

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

            # Add assistant's tool calls and tool results to message history
            append_tool_messages(messages, current_tool_calls, tool_results,
                                 conversation.model_provider)

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
        if reasoning_content:
            extra_metadata['reasoning'] = reasoning_content

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
        logger.exception(f"Streaming error: {str(e)}")
        yield f"data: {json.dumps({'error': PUBLIC_ERROR_MESSAGE, 'type': 'error'})}\n\n"


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
            db=db,
            enable_tools=request.enable_tools,
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

        # Build tools for the completion call (disabled in tool-free conditions)
        tools = None
        if request.enable_tools and service.supports_tools():
            tools = tool_registry.get_tools_for_provider(service.get_tools_format())

        # Multi-turn tool calling loop (same semantics as the streaming path):
        # model -> tool calls -> execute (only when enable_tools) -> results
        # appended -> next model call.
        max_iterations = 5
        iteration = 0
        full_response = ""
        final_response = None
        all_tool_calls = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        while iteration < max_iterations:
            iteration += 1
            kwargs = {}
            if tools:
                kwargs["tools"] = tools
            response = await service.chat_complete(
                messages=messages,
                model=conversation.model_name,
                temperature=conversation.temperature,
                max_tokens=conversation.max_tokens,
                **kwargs,
            )
            final_response = response
            full_response = response.get("content") or ""
            usage = response.get("usage") or {}
            for key in total_usage:
                total_usage[key] += usage.get(key, 0)

            raw_tool_calls = response.get("tool_calls") or []
            if not raw_tool_calls:
                break

            current_tool_calls = parse_tool_calls(raw_tool_calls)
            if not current_tool_calls:
                break

            tool_results, executed = await execute_guarded(current_tool_calls, request.enable_tools)
            if not executed:
                logger.warning("tool calls received but enable_tools=False; not executing")
                break

            for tr in tool_results:
                all_tool_calls.append({
                    'call': {
                        'id': tr.tool_id,
                        'name': tr.name,
                        'arguments': next((tc.arguments for tc in current_tool_calls if tc.id == tr.tool_id), {})
                    },
                    'result': {
                        'success': tr.success,
                        'result': tr.result,
                        'error': tr.error
                    }
                })

            append_tool_messages(messages, current_tool_calls, tool_results,
                                 conversation.model_provider)

        # Save assistant message with tool call metadata
        extra_metadata = {}
        if all_tool_calls:
            extra_metadata['tool_calls'] = all_tool_calls

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            prompt_tokens=total_usage["prompt_tokens"],
            completion_tokens=total_usage["completion_tokens"],
            total_tokens=total_usage["total_tokens"],
            extra_metadata=extra_metadata if extra_metadata else None
        )
        db.add(assistant_msg)

        # Update conversation statistics
        conversation.message_count += 2
        conversation.total_tokens += total_usage["total_tokens"]

        await db.commit()
        await db.refresh(assistant_msg)

        return ChatResponse(
            message_id=assistant_msg.id,
            content=full_response,
            model=final_response.get("model", conversation.model_name),
            prompt_tokens=total_usage["prompt_tokens"],
            completion_tokens=total_usage["completion_tokens"],
            total_tokens=total_usage["total_tokens"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=PUBLIC_ERROR_MESSAGE)
