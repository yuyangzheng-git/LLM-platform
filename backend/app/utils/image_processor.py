from PIL import Image
import base64
import io
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processor for image files"""

    @staticmethod
    async def compress_image(
        image_path: str,
        max_size: Tuple[int, int] = (1024, 1024),
        quality: int = 85
    ) -> bool:
        """
        Compress and resize image

        Args:
            image_path: Path to image file
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)

        Returns:
            Success status
        """
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background

                # Resize if needed
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save with compression
                img.save(image_path, optimize=True, quality=quality)

            return True

        except Exception as e:
            logger.error(f"Image compression error: {str(e)}")
            return False

    @staticmethod
    async def image_to_base64(image_path: str) -> Optional[str]:
        """
        Convert image to base64 string

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded string or None on error
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Base64 conversion error: {str(e)}")
            return None

    @staticmethod
    async def get_image_info(image_path: str) -> Optional[dict]:
        """
        Get image metadata

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with width, height, format, mode
        """
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                }
        except Exception as e:
            logger.error(f"Get image info error: {str(e)}")
            return None

    @staticmethod
    async def create_thumbnail(
        image_path: str,
        output_path: str,
        size: Tuple[int, int] = (200, 200)
    ) -> bool:
        """
        Create thumbnail for image

        Args:
            image_path: Path to source image
            output_path: Path to save thumbnail
            size: Thumbnail dimensions

        Returns:
            Success status
        """
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background

                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(output_path, optimize=True, quality=85)

            return True

        except Exception as e:
            logger.error(f"Thumbnail creation error: {str(e)}")
            return False
