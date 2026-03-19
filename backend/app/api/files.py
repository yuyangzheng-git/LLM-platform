from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.file_attachment import FileAttachment
from app.models.message import Message
from app.services.file_handler import FileHandler
from app.schemas.models import FileUploadResponse

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    message_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file
    If message_id is provided, attach to that message
    Otherwise, create orphan attachment that can be linked later
    """
    # Verify message exists if message_id provided
    if message_id:
        query = select(Message).where(Message.id == message_id)
        result = await db.execute(query)
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

    # Save file
    success, message_text, file_info = await FileHandler.save_upload_file(file)

    if not success:
        raise HTTPException(status_code=400, detail=message_text)

    # Create file attachment record
    attachment = FileAttachment(
        message_id=message_id,
        original_filename=file_info["original_filename"],
        stored_filename=file_info["stored_filename"],
        file_path=file_info["file_path"],
        file_type=file_info["file_type"],
        mime_type=file_info["mime_type"],
        file_size=file_info["file_size"],
        processed=bool(file_info.get("processed_content")),
        processed_content=file_info.get("processed_content"),
    )

    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    return attachment


@router.post("/upload/batch", response_model=List[FileUploadResponse], status_code=201)
async def upload_files_batch(
    files: List[UploadFile] = File(...),
    message_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload multiple files at once"""
    import logging
    logger = logging.getLogger(__name__)

    # Verify message exists if message_id provided
    if message_id:
        query = select(Message).where(Message.id == message_id)
        result = await db.execute(query)
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

    attachments = []
    failed_files = []

    for file in files:
        # 🔍 调试：记录实际接收到的 MIME 类型
        logger.info(f"📁 上传文件: {file.filename}, MIME类型: {file.content_type}")

        # Save file
        success, message_text, file_info = await FileHandler.save_upload_file(file)

        if not success:
            # Record failed file with detailed error
            error_detail = f"{file.filename} (类型:{file.content_type}): {message_text}"
            failed_files.append(error_detail)
            logger.error(f"❌ 文件上传失败 - {error_detail}")
            continue

        # Create file attachment record
        attachment = FileAttachment(
            message_id=message_id,
            original_filename=file_info["original_filename"],
            stored_filename=file_info["stored_filename"],
            file_path=file_info["file_path"],
            file_type=file_info["file_type"],
            mime_type=file_info["mime_type"],
            file_size=file_info["file_size"],
            processed=bool(file_info.get("processed_content")),
            processed_content=file_info.get("processed_content"),
        )

        db.add(attachment)
        attachments.append(attachment)

    # If all files failed, raise error
    if not attachments and failed_files:
        raise HTTPException(
            status_code=400,
            detail=f"所有文件上传失败: {'; '.join(failed_files)}"
        )

    # If some files failed, log warning
    if failed_files:
        logger.warning(f"部分文件上传失败 ({len(failed_files)}/{len(files)}): {'; '.join(failed_files)}")

    await db.commit()

    # Refresh all attachments
    for attachment in attachments:
        await db.refresh(attachment)

    return attachments


@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get file information"""
    query = select(FileAttachment).where(FileAttachment.id == file_id)
    result = await db.execute(query)
    attachment = result.scalar_one_or_none()

    if not attachment:
        raise HTTPException(status_code=404, detail="File not found")

    return attachment


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a file"""
    query = select(FileAttachment).where(FileAttachment.id == file_id)
    result = await db.execute(query)
    attachment = result.scalar_one_or_none()

    if not attachment:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete file from disk
    await FileHandler.delete_file(attachment.file_path)

    # Delete database record
    await db.delete(attachment)
    await db.commit()

    return None
