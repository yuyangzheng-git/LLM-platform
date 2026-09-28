"""
Smoke tests for application configuration and model-provider setup.
Run: python -m pytest tests/ -v  (from the backend directory)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings


def test_app_defaults():
    assert settings.APP_NAME == "LLM Chat Platform"
    assert settings.PORT == 3211
    assert settings.DATABASE_URL.startswith("sqlite+aiosqlite:///")
    assert settings.DEBUG in (True, False)


def test_llm_provider_config_shape():
    for field in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
        value = getattr(settings, field, "")
        assert isinstance(value, str)


def test_allowed_origins_non_empty():
    origins = settings.ALLOWED_ORIGINS
    if isinstance(origins, str):
        origins = [o.strip() for o in origins.split(",") if o.strip()]
    assert len(origins) > 0
    assert any("localhost" in o for o in origins)


def test_file_upload_limits_sane():
    assert settings.MAX_FILE_SIZE > 0
    assert settings.MAX_FILE_SIZE <= 1024 * 1024 * 1024
    assert len(settings.ALLOWED_FILE_TYPES) > 0


def test_encryption_key_documented():
    """ENCRYPTION_KEY should exist as a settings field so the app fails fast if missing."""
    assert hasattr(settings, "ENCRYPTION_KEY")
