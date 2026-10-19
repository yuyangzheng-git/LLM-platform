"""
Alembic migrations: fresh databases are built from migrations, legacy
databases created by the old create_all() startup are adopted, and the
migrated schema matches the ORM models.
"""
import os
import sqlite3
import sys

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.database import Base, _upgrade_to_head
import app.models.conversation  # noqa: F401
import app.models.file_attachment  # noqa: F401
import app.models.message  # noqa: F401
import app.models.model_config  # noqa: F401

# Legacy schema: message_id NOT NULL, no alembic_version table
LEGACY_SQL = """
CREATE TABLE conversations (id INTEGER PRIMARY KEY, title VARCHAR(255) NOT NULL,
  model_provider VARCHAR(50) NOT NULL, model_name VARCHAR(100) NOT NULL,
  system_prompt TEXT, temperature FLOAT, max_tokens INTEGER, top_p FLOAT,
  message_count INTEGER, total_tokens INTEGER, extra_metadata JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX ix_conversations_id ON conversations (id);
CREATE TABLE model_configs (id INTEGER PRIMARY KEY, provider VARCHAR(50) NOT NULL UNIQUE,
  api_key TEXT, api_base_url VARCHAR(512), organization_id VARCHAR(255),
  available_models JSON, default_model VARCHAR(100), default_temperature FLOAT,
  default_max_tokens INTEGER, enabled BOOLEAN, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX ix_model_configs_id ON model_configs (id);
CREATE TABLE messages (id INTEGER PRIMARY KEY,
  conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL, content TEXT NOT NULL, prompt_tokens INTEGER,
  completion_tokens INTEGER, total_tokens INTEGER, extra_metadata JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX ix_messages_id ON messages (id);
CREATE INDEX ix_messages_conversation_id ON messages (conversation_id);
CREATE TABLE file_attachments (id INTEGER PRIMARY KEY,
  message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  original_filename VARCHAR(255) NOT NULL, stored_filename VARCHAR(255) NOT NULL UNIQUE,
  file_path VARCHAR(512) NOT NULL, file_type VARCHAR(50) NOT NULL,
  mime_type VARCHAR(100) NOT NULL, file_size INTEGER NOT NULL, processed BOOLEAN,
  processed_content TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX ix_file_attachments_id ON file_attachments (id);
CREATE INDEX ix_file_attachments_message_id ON file_attachments (message_id);
INSERT INTO conversations (id, title, model_provider, model_name) VALUES (1, 'kept', 'openai', 'gpt');
"""


async def _migrate(db_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async with engine.begin() as conn:
        await conn.run_sync(_upgrade_to_head)

    def inspect_db(sync_conn):
        insp = inspect(sync_conn)
        nullable = {c["name"]: c["nullable"] for c in insp.get_columns("file_attachments")}
        diff = compare_metadata(MigrationContext.configure(sync_conn), Base.metadata)
        version = sync_conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar()
        return nullable, diff, version

    async with engine.connect() as conn:
        result = await conn.run_sync(inspect_db)
    await engine.dispose()
    return result


async def test_fresh_database_matches_models(tmp_path):
    nullable, diff, version = await _migrate(tmp_path / "fresh.db")
    assert version == "0002"
    assert nullable["message_id"] is True
    assert diff == []


async def test_legacy_database_is_adopted_and_upgraded(tmp_path):
    db_path = tmp_path / "legacy.db"
    with sqlite3.connect(db_path) as conn:
        conn.executescript(LEGACY_SQL)

    nullable, _, version = await _migrate(db_path)
    assert version == "0002"
    assert nullable["message_id"] is True
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT title FROM conversations").fetchone() == ("kept",)
