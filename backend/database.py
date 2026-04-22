import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "hobby_tracker.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hobbies TEXT NOT NULL,
                interests TEXT NOT NULL,
                document_name TEXT,
                document_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # migrate existing DBs that lack document columns
        cols = {r[1] for r in conn.execute("PRAGMA table_info(profiles)")}
        if "document_name" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN document_name TEXT")
        if "document_data" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN document_data BLOB")
        conn.commit()
