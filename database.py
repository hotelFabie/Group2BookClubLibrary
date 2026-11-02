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

def get_loans_by_member_id(member_id: int) -> list[dict]:
    "Finds all loans by member id."
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM loans WHERE member_id = ?", (member_id,))
    rows = cursor.fetchall()

    return [dict(row) for row in rows]


def fetch_all_members() -> list[dict]:
    """Return all members as a list of dicts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, name, email, phone, joined_date FROM members"
        ).fetchall()
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

def fetch_member(member_id: int) -> dict | None:
    """Return one member by id, or None if not found."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT id, name, email, phone, joined_date FROM members WHERE id = ?",
            (member_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insert_member(name: str, email: str, phone: str | None) -> dict:
    """Insert a new member and return the created row as a dict.

    Raises sqlite3.IntegrityError on duplicate email.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone),
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, name, email, phone, joined_date FROM members WHERE id = ?",
            (new_id,),
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


def update_member_fields(member_id: int, updates: dict) -> dict | None:
    """Update the given fields on a member. Returns the updated row as a dict,
    or None if no member with that id exists.

    Raises sqlite3.IntegrityError on duplicate email.
    """
    columns = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [member_id]

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            f"UPDATE members SET {columns} WHERE id = ?",
            values,
        )
        if cursor.rowcount == 0:
            return None
        conn.commit()
        row = conn.execute(
            "SELECT id, name, email, phone, joined_date FROM members WHERE id = ?",
            (member_id,),
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


def fetch_all_loans() -> list[dict]:
    """Return all loans."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, book_id, member_id, loan_date, due_date, return_date FROM loans"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_loan(loan_id: int) -> dict | None:
    """Return one loan by id, or None if not found."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT id, book_id, member_id, loan_date, due_date, return_date "
            "FROM loans WHERE id = ?",
            (loan_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def has_active_loan_for_book(book_id: int) -> bool:
    """Return True if the book has an active (not returned) loan."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM loans WHERE book_id = ? AND return_date IS NULL LIMIT 1",
            (book_id,),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def insert_loan(book_id: int, member_id: int, loan_date: str, due_date: str) -> dict:
    """Insert a new loan. Raises IntegrityError on bad foreign keys."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "INSERT INTO loans (book_id, member_id, loan_date, due_date) "
            "VALUES (?, ?, ?, ?)",
            (book_id, member_id, loan_date, due_date),
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, book_id, member_id, loan_date, due_date, return_date "
            "FROM loans WHERE id = ?",
            (new_id,),
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


def update_loan_fields(loan_id: int, updates: dict) -> dict | None:
    """Update given fields on a loan. Returns the row, or None if not found."""
    columns = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [loan_id]

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            f"UPDATE loans SET {columns} WHERE id = ?",
            values,
        )
        if cursor.rowcount == 0:
            return None
        conn.commit()
        row = conn.execute(
            "SELECT id, book_id, member_id, loan_date, due_date, return_date "
            "FROM loans WHERE id = ?",
            (loan_id,),
        ).fetchone()
        return dict(row)
    finally:
        conn.close()

def return_loan(loan_id: int) -> dict | None:
    """Updates the return date to whatever the date is when attempting a return."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE loans SET return_date = ? WHERE id = ?",
            (datetime.date.today().isoformat(), loan_id)
        )
        if cursor.rowcount == 0:
            return None 

        conn.commit()

        #Return for external methods using this.
        cursor.execute(
            "SELECT * FROM loans WHERE id = ?", (loan_id,)
        )

        row = cursor.fetchone()

        return dict(row)
    
    finally:
        conn.close()