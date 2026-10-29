from pathlib import Path
import sqlite3
from datetime import date

DB_PATH = Path(__file__).parent / "library.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def fetch_all_authors() -> list[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM authors")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def insert_author(
    name: str, 
    open_library_key: str | None, 
    birth_date: date | None, 
    death_date: date | None
) -> dict | None:
     
    conn = get_connection()
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
    finally:
        conn.close()

def update_author(author_id: int, update_data: dict) -> dict | None:
    """Dynamically updates an author and returns the modified record."""   
    if not update_data:
        return None

    # Build the dynamic SQL string (e.g., "name = ?, birth_date = ?")
    set_clauses = [f"{key} = ?" for key in update_data.keys()]
    set_clause_str = ", ".join(set_clauses)
    
    # Append the author_id to the end of the values list for the WHERE clause
    values = list(update_data.values())
    values.append(author_id)

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE authors SET {set_clause_str} WHERE id = ?",
            tuple(values)
        )
        
        # If no rows were changed, the ID doesn't exist
        if cursor.rowcount == 0:
            return None
            
        conn.commit()
        
        # Fetch and return the finalized record
        cursor.execute("SELECT * FROM authors WHERE id = ?", (author_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()