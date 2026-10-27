from pathlib import Path
import sqlite3


def get_connection():
    DB_PATH = Path(__file__).parent / "library.db"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
