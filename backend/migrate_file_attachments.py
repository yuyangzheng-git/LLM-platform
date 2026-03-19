"""Migration: Make message_id nullable in file_attachments table"""
import sqlite3
import os

def migrate():
    db_path = "./data/llm_chat.db"

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # SQLite doesn't support ALTER COLUMN directly
        # We need to recreate the table

        print("Starting migration...")

        # 1. Create new table with nullable message_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_attachments_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                original_filename VARCHAR(255) NOT NULL,
                stored_filename VARCHAR(255) NOT NULL UNIQUE,
                file_path VARCHAR(512) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                mime_type VARCHAR(100) NOT NULL,
                file_size INTEGER NOT NULL,
                processed BOOLEAN DEFAULT 0,
                processed_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
            )
        """)

        # 2. Copy data from old table to new table
        cursor.execute("""
            INSERT INTO file_attachments_new
            SELECT * FROM file_attachments
        """)

        # 3. Drop old table
        cursor.execute("DROP TABLE file_attachments")

        # 4. Rename new table to original name
        cursor.execute("ALTER TABLE file_attachments_new RENAME TO file_attachments")

        # 5. Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_file_attachments_id ON file_attachments(id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_file_attachments_message_id ON file_attachments(message_id)")

        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - message_id is now nullable")
        print("   - Files can be uploaded as orphans and linked later")

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
