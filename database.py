from pathlib import Path
import sqlite3


def get_connection():
    DB_PATH = Path(__file__).parent / "library.db"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


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

import datetime

#Gotta add the return indicator here + add a method.
def return_book(loan_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()

        #If anything is found. 
        #WIP: Not sure if this is the correct format?
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

        #WIP: Is this guaranteed to return anything?
        return dict(row)

    finally:
        conn.close()