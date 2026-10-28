from pathlib import Path
import sqlite3


def get_connection():
    DB_PATH = Path(__file__).parent / "library.db"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_loans_by_member_id(member_id : int) -> list[dict]:
    "Finds all loans by member id."
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM loans WHERE member_id = ?", (member_id,))
    rows = cursor.fetchall()

    return [dict(row) for row in rows]
