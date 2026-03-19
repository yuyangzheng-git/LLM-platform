from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float
from sqlalchemy.sql import func
from app.database import Base


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)

    # Provider information
    provider = Column(String(50), nullable=False, unique=True)  # openai, anthropic, gemini, generic

    # API configuration
    api_key = Column(Text, nullable=True)  # Encrypted
    api_base_url = Column(String(512), nullable=True)  # For generic OpenAI-compatible APIs
    organization_id = Column(String(255), nullable=True)  # For OpenAI

    # Available models (stored as JSON array)
    available_models = Column(JSON, nullable=True)

    # Default settings
    default_model = Column(String(100), nullable=True)
    default_temperature = Column(Float, default=0.7)
    default_max_tokens = Column(Integer, default=2000)

    # Status
    enabled = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ModelConfig(id={self.id}, provider={self.provider}, enabled={self.enabled})>"
