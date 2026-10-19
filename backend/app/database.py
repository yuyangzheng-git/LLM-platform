from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"

# Revision matching the schema the old create_all() startup produced
BASELINE_REVISION = "0001"

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for models
Base = declarative_base()


# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def _upgrade_to_head(sync_conn) -> None:
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(ALEMBIC_INI))
    cfg.attributes["connection"] = sync_conn

    tables = set(inspect(sync_conn).get_table_names())
    if "alembic_version" not in tables and "conversations" in tables:
        # Database created before migrations existed: adopt it at the baseline
        command.stamp(cfg, BASELINE_REVISION)

    command.upgrade(cfg, "head")


# Initialize database: apply any pending Alembic migrations
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(_upgrade_to_head)
