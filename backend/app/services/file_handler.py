import os
import uuid
import aiofiles
from typing import Optional, Tuple
from fastapi import UploadFile
import logging

from app.config import settings
from app.utils.file_validator import FileValidator
from app.utils.image_processor import ImageProcessor
from app.utils.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class FileHandler:
    """Handler for file upload and processing"""

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Generate unique filename while preserving extension

        Args:
            original_filename: Original filename

        Returns:
            Unique filename
        """
        ext = os.path.splitext(original_filename)[1]
        unique_id = uuid.uuid4().hex
        return f"{unique_id}{ext}"

    @staticmethod
    def get_file_type(mime_type: str) -> str:
        """
        Determine file type category from MIME type

        Args:
            mime_type: MIME type string

        Returns:
            File type category (image, pdf, text, document)
        """
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type == "application/pdf":
            return "pdf"
        elif mime_type.startswith("text/"):
            return "text"
        else:
            return "document"

    @staticmethod
    async def save_upload_file(upload_file: UploadFile) -> Tuple[bool, str, Optional[dict]]:
        """
        Save uploaded file to disk

        Args:
            upload_file: FastAPI UploadFile object

        Returns:
            Tuple of (success, message, file_info_dict)
        """
        try:
            # Read file content
            content = await upload_file.read()
            file_size = len(content)

            # Validate file
            is_valid, error = FileValidator.validate_file(
                upload_file.filename,
                file_size,
                upload_file.content_type
            )

            if not is_valid:
                return False, error, None

            # Generate unique filename
            stored_filename = FileHandler.generate_unique_filename(upload_file.filename)
            file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            # Determine file type
            file_type = FileHandler.get_file_type(upload_file.content_type)

            # Process file based on type
            processed_content = None

            if file_type == "image":
                # Compress image
                await ImageProcessor.compress_image(file_path)

            elif file_type == "pdf":
                # Extract text from PDF
                processed_content = await PDFProcessor.extract_text(file_path)

            elif file_type == "text":
                # Read text content
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    processed_content = await f.read()

            file_info = {
                "original_filename": upload_file.filename,
                "stored_filename": stored_filename,
                "file_path": file_path,
                "file_type": file_type,
                "mime_type": upload_file.content_type,
                "file_size": file_size,
                "processed_content": processed_content,
            }

            return True, "File uploaded successfully", file_info

        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return False, f"File upload failed: {str(e)}", None

    @staticmethod
    async def delete_file(file_path: str) -> bool:
        """
        Delete file from disk

        Args:
            file_path: Path to file

        Returns:
            Success status
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            return False

    @staticmethod
    async def get_file_content(file_path: str, file_type: str) -> Optional[str]:
        """
        Get file content based on type

        Args:
            file_path: Path to file
            file_type: Type of file (image, pdf, text)

        Returns:
            File content as string or base64
        """
        try:
            if file_type == "image":
                return await ImageProcessor.image_to_base64(file_path)

            elif file_type == "pdf":
                return await PDFProcessor.extract_text(file_path)

            elif file_type == "text":
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    return await f.read()

            return None

        except Exception as e:
            logger.error(f"Get file content error: {str(e)}")
            return None
