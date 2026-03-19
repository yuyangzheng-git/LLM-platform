from typing import Tuple
import mimetypes
import os
from app.config import settings


class FileValidator:
    """Validator for uploaded files"""

    @staticmethod
    def validate_file_type(filename: str, mime_type: str) -> Tuple[bool, str]:
        """
        Validate file type ONLY based on extension (ignore MIME type completely)

        Args:
            filename: Original filename
            mime_type: MIME type of the file (ignored, for compatibility)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # 获取文件扩展名
        ext = os.path.splitext(filename.lower())[1]

        # 定义支持的扩展名 - 只检查这个！
        supported_extensions = {
            # Images
            ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
            # Documents
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            # Text
            ".txt", ".md", ".csv", ".html", ".htm", ".json", ".xml",
        }

        # 只检查扩展名，完全忽略 MIME 类型
        if ext not in supported_extensions:
            supported_list = ", ".join(sorted(supported_extensions))
            return False, f"不支持的文件类型 {ext}。支持的类型: {supported_list}"

        return True, ""

    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, str]:
        """
        Validate file size

        Args:
            file_size: Size of file in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size > settings.MAX_FILE_SIZE:
            max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            current_mb = file_size / (1024 * 1024)
            return False, f"文件大小 {current_mb:.1f}MB 超过限制 {max_mb:.0f}MB"

        if file_size == 0:
            return False, "文件为空"

        return True, ""

    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """
        Validate filename for security

        Args:
            filename: Original filename

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            return False, "Invalid filename: path traversal detected"

        # Check for empty filename
        if not filename or filename.strip() == "":
            return False, "Filename cannot be empty"

        # Check filename length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"

        return True, ""

    @classmethod
    def validate_file(
        cls,
        filename: str,
        file_size: int,
        mime_type: str
    ) -> Tuple[bool, str]:
        """
        Comprehensive file validation

        Args:
            filename: Original filename
            file_size: File size in bytes
            mime_type: MIME type

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate filename
        is_valid, error = cls.validate_filename(filename)
        if not is_valid:
            return False, error

        # Validate file size
        is_valid, error = cls.validate_file_size(file_size)
        if not is_valid:
            return False, error

        # Validate file type
        is_valid, error = cls.validate_file_type(filename, mime_type)
        if not is_valid:
            return False, error

        return True, ""
