"""Initialize default OpenAI configuration in database"""
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import get_db, init_db
from app.models.model_config import ModelConfig
from app.config import settings


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key"""
    key = settings.ENCRYPTION_KEY.encode() if settings.ENCRYPTION_KEY else Fernet.generate_key()
    cipher = Fernet(key)
    return cipher.encrypt(api_key.encode()).decode()


async def init_default_config():
    """Initialize default OpenAI configuration"""
    await init_db()

    # Get database session
    async for db in get_db():
        # Check if OpenAI config already exists
        result = await db.execute(
            select(ModelConfig).where(ModelConfig.provider == "openai")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("OpenAI configuration already exists, updating...")
            existing.api_key = encrypt_api_key(os.getenv("OPENAI_API_KEY", ""))
            existing.api_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            existing.default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")
            existing.enabled = True
            existing.available_models = [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-4-32k",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-4-vision-preview",
                "o1-preview",
                "o1-mini",
            ]
        else:
            print("Creating new OpenAI configuration...")
            config = ModelConfig(
                provider="openai",
                api_key=encrypt_api_key(os.getenv("OPENAI_API_KEY", "")),
                api_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                default_model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini"),
                enabled=True,
                available_models=[
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "gpt-4-turbo-preview",
                    "gpt-4",
                    "gpt-4-32k",
                    "gpt-3.5-turbo",
                    "gpt-3.5-turbo-16k",
                    "gpt-4-vision-preview",
                    "o1-preview",
                    "o1-mini",
                ],
                default_temperature=0.7,
                default_max_tokens=2000,
            )
            db.add(config)

        await db.commit()
        print("✅ Default OpenAI configuration initialized successfully!")
        break


if __name__ == "__main__":
    asyncio.run(init_default_config())
