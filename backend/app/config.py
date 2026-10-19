from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "LLM Chat Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 3211

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/llm_chat.db"

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3212",
        "http://127.0.0.1:3212",
    ]

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 104857600  # 100MB (increased from 10MB)
    # Deprecated: not used for validation. Uploads are checked by file
    # extension in app/utils/file_validator.py. Kept so existing .env files
    # that still set it keep loading.
    ALLOWED_FILE_TYPES: Union[List[str], str] = [
        # Images
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/gif",
        "image/webp",
        "image/bmp",
        "image/svg+xml",
        # Documents - PDF
        "application/pdf",
        # Documents - Word
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/word",
        "application/vnd.ms-word",
        # Documents - Excel
        "application/vnd.ms-excel",  # .xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/excel",
        "application/x-excel",
        "application/x-msexcel",
        # Documents - PowerPoint
        "application/vnd.ms-powerpoint",  # .ppt
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
        "application/powerpoint",
        # Text formats
        "text/plain",
        "text/markdown",
        "text/csv",
        "text/html",
        "application/json",
        "application/xml",
        "text/xml",
        # Generic fallback for Office documents
        "application/octet-stream",  # Some browsers use this for unknown types
    ]

    # Encryption
    ENCRYPTION_KEY: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # Optional API Keys (can be configured via UI)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_DEFAULT_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # SearxNG Configuration
    SEARXNG_BASE_URL: str = "http://searxng:8080"
    SEARXNG_ENABLED: bool = True
    SEARXNG_MAX_RESULTS: int = 5
    SEARXNG_TIMEOUT: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @field_validator('ALLOWED_FILE_TYPES', mode='before')
    @classmethod
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(',')]
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        db_path = self.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        log_dir = os.path.dirname(self.LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)


settings = Settings()
