"""Book Club Library API."""

import database 
from datetime import datetime 
from fastapi import FastAPI, HTTPException, status

from models import BookCreate

app = FastAPI(title="Book Club Library API")


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Book Club Library API"}

@app.get("/members/{member_id}/loans")
def get_member_loans(member_id : int):
    "Gets loans in raw dictionary format, and adds visible status."

    raw_loans = database.get_loans_by_member_id(member_id)

    loans = []

    for loan in raw_loans:
        if loan["return_date"] is not None:
            loan["status"] = "Returned"
        elif datetime.strptime(loan["due_date"], "%Y-%m-%d") < datetime.now(): 
            loan["status"] = "Overdue"
        else:
            loan["status"] = "Borrowing"

        loans.append(loan)     
    
    return loans

def find_book(book_id: int):
    """ Finds a book by id. """
    
    book = database.get_book_by_id(book_id)

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    return book

@app.get("/books")
def get_books(author: str | None = None):
    """Endpoint for reading all the books in the Library. Query parameter: 'author'"""
    if author is not None:
        author = author.strip()
        if not author or not author[0].isalpha():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Author must be the name of the author!",
            )
        
    books = database.get_books(author)

    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            datail="No books found!")
    
    return books

@app.get("/books/{book_id}")
def get_book(book_id: int):
    """Endpoint for reading a book by id"""

    return find_book(book_id)



# TODO fixa post och delete för books
# Fixa också put i mån av tid 


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    """Endpoint for adding a new book to the Library."""

    if not book.title.strip() or not book.author.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and author are required!",
        )
    
    new_book : BookCreate = {}

    if book.title:
        new_book["title"] = book.title
    if book.first_publish_year:
        new_book["first_publish_year"] = book.first_publish_year
    if book.open_library_key:
        new_book["open_library_key"] = book.open_library_key
    if book.open_library_key:
        new_book["isbn"] = book.isbn
    if book.cover_id:
        new_book["cover_id"] = book.cover_id
    if book.author:
        new_book["author"] = book.author
    
    try:    
        created_book = database.create_book(new_book)
    except database.AuthorNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't save to database!")

    return created_book

