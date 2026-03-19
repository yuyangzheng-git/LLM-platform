from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from cryptography.fernet import Fernet

from app.database import get_db
from app.models.model_config import ModelConfig
from app.schemas.models import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse
)
from app.services.llm.factory import LLMServiceFactory
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Encryption helper
def get_cipher():
    """Get encryption cipher"""
    if not settings.ENCRYPTION_KEY:
        # Generate a key if not set (for development only)
        key = Fernet.generate_key()
        logger.warning("No encryption key set, using temporary key")
        return Fernet(key)
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key"""
    cipher = get_cipher()
    return cipher.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key"""
    cipher = get_cipher()
    return cipher.decrypt(encrypted_key.encode()).decode()


@router.get("/configs", response_model=List[ModelConfigResponse])
async def list_model_configs(
    db: AsyncSession = Depends(get_db)
):
    """List all model configurations"""
    query = select(ModelConfig).order_by(ModelConfig.provider)
    result = await db.execute(query)
    configs = result.scalars().all()

    return configs


@router.post("/configs", response_model=ModelConfigResponse, status_code=201)
async def create_or_update_config(
    config_data: ModelConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create or update model configuration"""
    # Check if config already exists for provider
    query = select(ModelConfig).where(
        ModelConfig.provider == config_data.provider
    )
    result = await db.execute(query)
    existing_config = result.scalar_one_or_none()

    # Encrypt API key
    encrypted_key = encrypt_api_key(config_data.api_key)

    if existing_config:
        # Update existing config
        existing_config.api_key = encrypted_key
        if config_data.api_base_url:
            existing_config.api_base_url = config_data.api_base_url
        if config_data.organization_id:
            existing_config.organization_id = config_data.organization_id
        if config_data.default_model:
            existing_config.default_model = config_data.default_model
        existing_config.default_temperature = config_data.default_temperature
        existing_config.default_max_tokens = config_data.default_max_tokens
        existing_config.enabled = config_data.enabled

        await db.commit()
        await db.refresh(existing_config)
        return existing_config

    else:
        # Create new config
        # Try to get available models
        try:
            service = LLMServiceFactory.create_service(
                provider=config_data.provider,
                api_key=config_data.api_key,
                api_base_url=config_data.api_base_url,
                organization_id=config_data.organization_id,
            )
            available_models = service.get_available_models()
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            available_models = []

        config = ModelConfig(
            provider=config_data.provider,
            api_key=encrypted_key,
            api_base_url=config_data.api_base_url,
            organization_id=config_data.organization_id,
            available_models=available_models,
            default_model=config_data.default_model,
            default_temperature=config_data.default_temperature,
            default_max_tokens=config_data.default_max_tokens,
            enabled=config_data.enabled,
        )

        db.add(config)
        await db.commit()
        await db.refresh(config)

        return config


@router.get("/configs/{provider}", response_model=ModelConfigResponse)
async def get_model_config(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """Get configuration for a specific provider"""
    query = select(ModelConfig).where(ModelConfig.provider == provider)
    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config for {provider} not found")

    return config


@router.put("/configs/{provider}", response_model=ModelConfigResponse)
async def update_model_config(
    provider: str,
    config_data: ModelConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update model configuration"""
    query = select(ModelConfig).where(ModelConfig.provider == provider)
    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config for {provider} not found")

    # Update fields
    update_data = config_data.model_dump(exclude_unset=True)

    if "api_key" in update_data:
        update_data["api_key"] = encrypt_api_key(update_data["api_key"])

    for field, value in update_data.items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)

    return config


@router.delete("/configs/{provider}", status_code=204)
async def delete_model_config(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete model configuration"""
    query = select(ModelConfig).where(ModelConfig.provider == provider)
    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config for {provider} not found")

    await db.delete(config)
    await db.commit()

    return None


@router.post("/test/{provider}")
async def test_model_connection(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """Test connection to model provider"""
    query = select(ModelConfig).where(ModelConfig.provider == provider)
    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config for {provider} not found")

    try:
        # Decrypt API key
        api_key = decrypt_api_key(config.api_key)

        # Create service and test connection
        service = LLMServiceFactory.create_service(
            provider=provider,
            api_key=api_key,
            api_base_url=config.api_base_url,
            organization_id=config.organization_id,
        )

        is_connected = await service.test_connection()

        return {
            "provider": provider,
            "connected": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed"
        }

    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        return {
            "provider": provider,
            "connected": False,
            "message": str(e)
        }


@router.get("/available/{provider}")
async def get_available_models(
    provider: str,
    db: AsyncSession = Depends(get_db)
):
    """Get available models for a provider"""
    query = select(ModelConfig).where(ModelConfig.provider == provider)
    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail=f"Config for {provider} not found")

    return {
        "provider": provider,
        "models": config.available_models or []
    }
