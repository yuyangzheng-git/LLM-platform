from pypdf import PdfReader
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processor for PDF files"""

    @staticmethod
    async def extract_text(pdf_path: str) -> Optional[str]:
        """
        Extract text content from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None on error
        """
        try:
            reader = PdfReader(pdf_path)
            text_content = []

            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1}: {str(e)}")
                    continue

            return "\n\n".join(text_content) if text_content else None

        except Exception as e:
            logger.error(f"PDF text extraction error: {str(e)}")
            return None

    @staticmethod
    async def get_pdf_info(pdf_path: str) -> Optional[Dict]:
        """
        Get PDF metadata

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with page_count, metadata, etc.
        """
        try:
            reader = PdfReader(pdf_path)

            info = {
                "page_count": len(reader.pages),
                "metadata": {},
            }

            # Extract metadata if available
            if reader.metadata:
                metadata = reader.metadata
                info["metadata"] = {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "creation_date": str(metadata.get("/CreationDate", "")),
                }

            return info

        except Exception as e:
            logger.error(f"PDF info extraction error: {str(e)}")
            return None

    @staticmethod
    async def extract_page_text(pdf_path: str, page_number: int) -> Optional[str]:
        """
        Extract text from specific PDF page

        Args:
            pdf_path: Path to PDF file
            page_number: Page number (0-indexed)

        Returns:
            Extracted text or None on error
        """
        try:
            reader = PdfReader(pdf_path)

            if page_number >= len(reader.pages):
                logger.error(f"Page {page_number} out of range")
                return None

            page = reader.pages[page_number]
            return page.extract_text()

        except Exception as e:
            logger.error(f"PDF page extraction error: {str(e)}")
            return None
