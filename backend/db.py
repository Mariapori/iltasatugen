"""
SQLite-tietokanta iltasatujen tallentamiseen.
"""

import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "iltasatuja.db"

def init_db():
    """Luo tietokanta ja taulut jos ei ole olemassa."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            audio_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    """Palaa SQLite-yhteys rivitehtaalla."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn
