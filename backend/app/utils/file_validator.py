from typing import Tuple
import os
from app.config import settings

# Extension -> MIME type. The extension is the source of truth; the
# browser-supplied Content-Type is not trusted.
SUPPORTED_EXTENSIONS = {
    # Images (SVG is excluded: it can carry scripts and cannot be processed)
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    # Documents
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    # Text
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".html": "text/html",
    ".htm": "text/html",
    ".json": "application/json",
    ".xml": "text/xml",
}


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
        ext = os.path.splitext(filename.lower())[1]

        # 只检查扩展名，完全忽略 MIME 类型
        if ext not in SUPPORTED_EXTENSIONS:
            supported_list = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            return False, f"不支持的文件类型 {ext}。支持的类型: {supported_list}"

        return True, ""

    @staticmethod
    def guess_mime_type(filename: str) -> str:
        """MIME type for a filename that already passed validate_file_type."""
        ext = os.path.splitext(filename.lower())[1]
        return SUPPORTED_EXTENSIONS.get(ext, "application/octet-stream")

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
