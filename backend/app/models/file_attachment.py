from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class FileAttachment(Base):
    __tablename__ = "file_attachments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True)

    # File information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(512), nullable=False)

    # File type and metadata
    file_type = Column(String(50), nullable=False)  # image, pdf, text, document
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)

    # Processing status
    processed = Column(Boolean, default=False)
    processed_content = Column(Text, nullable=True)  # Extracted text from PDF, OCR, etc.

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<FileAttachment(id={self.id}, filename={self.original_filename}, type={self.file_type})>"
