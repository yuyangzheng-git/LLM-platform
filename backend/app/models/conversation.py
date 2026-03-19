from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)

    # Model information
    model_provider = Column(String(50), nullable=False)  # openai, anthropic, gemini, generic
    model_name = Column(String(100), nullable=False)

    # Model parameters
    system_prompt = Column(Text, nullable=True)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    top_p = Column(Float, default=1.0)

    # Statistics
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Extra metadata
    extra_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title}, model={self.model_provider}/{self.model_name})>"
