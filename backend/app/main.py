from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from loguru import logger

from app.config import settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting LLM Chat Platform...")
    await init_db()
    logger.info("Database initialized")

    # Register tools
    from app.tools.search_tool import register_search_tool
    from app.tools.datetime_tool import register_datetime_tool
    from app.tools.location_tool import register_location_tools
    from app.tools.web_scraper_tool import register_web_scraper_tool

    register_search_tool()
    register_datetime_tool()
    register_location_tools()
    register_web_scraper_tool()
    logger.info("All tools registered successfully")

    yield
    # Shutdown
    logger.info("Shutting down LLM Chat Platform...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    )


@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to LLM Chat Platform API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }
    )


# Register API routers
from app.api import chat, conversations, files, models, generation

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(generation.router, prefix="/api/v1/generation", tags=["generation"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
