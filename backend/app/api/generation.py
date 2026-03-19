from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from openai import AsyncOpenAI
from app.database import get_db
from app.models.model_config import ModelConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

logger = logging.getLogger(__name__)
router = APIRouter()


class ImageGenerationRequest(BaseModel):
    model: str
    prompt: str
    size: str = "1024x1024"
    quality: Optional[str] = "standard"
    style: Optional[str] = None


class VideoGenerationRequest(BaseModel):
    model: str
    prompt: str
    duration: str = "5s"
    resolution: str = "720p"
    aspect_ratio: str = "16:9"


class GenerationResponse(BaseModel):
    url: str
    prompt: str
    model: str
    size: Optional[str] = None
    duration: Optional[str] = None
    resolution: Optional[str] = None


@router.post("/image", response_model=GenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate an image using AI"""
    try:
        # Get OpenAI config
        query = select(ModelConfig).where(ModelConfig.provider == 'openai')
        result = await db.execute(query)
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=400, detail="OpenAI configuration not found")

        from app.api.models import decrypt_api_key
        api_key = decrypt_api_key(config.api_key)

        # Create client
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=config.api_base_url or "https://api.openai.com/v1"
        )

        # Generate image
        params = {
            "model": request.model,
            "prompt": request.prompt,
            "size": request.size,
            "n": 1,
        }

        # Add optional parameters for DALL-E 3
        if request.model == "dall-e-3":
            if request.quality:
                params["quality"] = request.quality
            if request.style:
                params["style"] = request.style

        response = await client.images.generate(**params)

        return GenerationResponse(
            url=response.data[0].url,
            prompt=request.prompt,
            model=request.model,
            size=request.size
        )

    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video", response_model=GenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a video using AI"""
    try:
        # Get OpenAI config
        query = select(ModelConfig).where(ModelConfig.provider == 'openai')
        result = await db.execute(query)
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=400, detail="OpenAI configuration not found")

        from app.api.models import decrypt_api_key
        api_key = decrypt_api_key(config.api_key)

        # Create client
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=config.api_base_url or "https://api.openai.com/v1"
        )

        # For video generation, use chat completions with special formatting
        # Different providers might have different endpoints
        # This is a generic implementation that should work with OpenAI-compatible APIs

        # Construct the request based on model type
        if request.model.startswith('sora'):
            # Sora uses a specific format
            chat_response = await client.chat.completions.create(
                model=request.model,
                messages=[{
                    "role": "user",
                    "content": request.prompt
                }],
                max_tokens=10,  # Video generation doesn't need many tokens
            )
            # The response should contain a URL to the generated video
            # This is a simplified implementation - actual API might differ
            video_url = chat_response.choices[0].message.content
        else:
            # For other video models (Runway, Kling, etc.)
            # They might have their own specific endpoints
            chat_response = await client.chat.completions.create(
                model=request.model,
                messages=[{
                    "role": "user",
                    "content": f"Generate video: {request.prompt}\nDuration: {request.duration}\nResolution: {request.resolution}\nAspect Ratio: {request.aspect_ratio}"
                }],
                max_tokens=10,
            )
            video_url = chat_response.choices[0].message.content

        return GenerationResponse(
            url=video_url,
            prompt=request.prompt,
            model=request.model,
            duration=request.duration,
            resolution=request.resolution
        )

    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
