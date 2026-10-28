from pathlib import Path
import sqlite3
from datetime import date

DB_PATH = Path(__file__).parent / "library.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def insert_author(
    name: str, 
    open_library_key: str | None, 
    birth_date: date | None, 
    death_date: date | None
) -> dict | None:
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO authors (name, open_library_key, birth_date, death_date) 
                VALUES (?, ?, ?, ?)
                """,
                (name, open_library_key, birth_date, death_date)
            )
            conn.commit()
            
            # Fetch the newly generated record using the inserted ID
            new_id = cursor.lastrowid
            cursor.execute("SELECT * FROM authors WHERE id = ?", (new_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except sqlite3.IntegrityError:
            
            return None