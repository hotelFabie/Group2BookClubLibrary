from pathlib import Path
import sqlite3
from typing import Any

from models import BookCreate

class AuthorNotFoundError(Exception):
    """Raised when the given author does not exist."""

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

def get_book_by_id(book_id : int) -> dict:
    "Find book by id."
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()


        cursor.execute("SELECT b.title, b.first_publish_year, b.open_library_key, b.cover_id," \
                        " b.isbn, b.subject, GROUP_CONCAT(a.name, ', ') as author "
                        + "FROM books b JOIN book_authors ba ON ba.book_id "+
                        "= b.id JOIN authors a ON a.id = ba.author_id WHERE b.id = ? "
                        "GROUP BY b.id", (book_id,),)
        row = cursor.fetchone()

        return dict(row) if row else None
    finally:
        conn.close()

def get_books(author : str | None = None):
    "Gets all the books."
    conn = get_connection()

    try:
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        if author:
            cursor.execute(
                "SELECT b.title, b.first_publish_year, b.open_library_key, b.cover_id," \
                        " b.isbn, b.subject, GROUP_CONCAT(a.name, ', ') as author "
                        + "FROM books b JOIN book_authors ba ON ba.book_id "+
                        "= b.id JOIN authors a ON a.id = ba.author_id WHERE a.name LIKE ? "
                        "GROUP BY b.id",
                (f"%{author}%",),
            )

        else:
            cursor.execute("SELECT b.title, b.first_publish_year, b.open_library_key, b.cover_id," \
                        " b.isbn, b.subject, GROUP_CONCAT(a.name, ', ') as author "
                        + "FROM books b JOIN book_authors ba ON ba.book_id "+
                        "= b.id JOIN authors a ON a.id = ba.author_id GROUP BY b.id")
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def create_book(book : BookCreate) -> dict:
    "Adds a new book and links it to its author."
    
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Reuse the author if they already exist, otherwise create them
        cursor.execute("SELECT id FROM authors WHERE name = ?", (book.get("author"),))

        row = cursor.fetchone()
        if row is None:
            raise AuthorNotFoundError(f"Author '{book.get("author")}' not found!")
        else:
            author_id = 1
        print("-------------A----------") 

        ### TODO något fel här nedan. Hitta felet !!! + fixa delete och put också kanske
        cursor.execute(
        """
        INSERT INTO books (title, first_publish_year, open_library_key, cover_id, isbn, subject)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ("", 1999, "", 1, "", ""),)
        # cursor.execute(
        #     "INSERT INTO books (title, first_publish_year, open_library_key, "
        #     "cover_id, isbn, subject) VALUES (?, ?, ?, ?, ?, ?)",
        #     (book.title, book.first_publish_year, book.open_library_key,
        #      book.cover_id, book.isbn, book.subject),
        # )
        print("-------------B----------") 

        book_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)",
            (book_id, author_id),
        )
        print("------------C----------") 

        conn.commit()
    except Exception:
        conn.rollback()
        raise 
    finally:
        conn.close()

    return get_book_by_id(book_id)

