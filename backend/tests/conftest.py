"""
Test isolation setup:
- points the database at a temporary SQLite file (no dependency on the
  developer's local llm_chat.db)
- points uploads at a temporary directory
- sets a stable ENCRYPTION_KEY so encrypt/decrypt round-trips

Must run before any test module imports `app.*`.
"""
import os
import tempfile

from cryptography.fernet import Fernet

_TMP = tempfile.mkdtemp(prefix="llm_platform_test_")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP}/test_llm_chat.db"
os.environ["UPLOAD_DIR"] = _TMP
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
