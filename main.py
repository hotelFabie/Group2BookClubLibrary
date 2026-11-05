"""Book Club Library API."""
import os
import database 
import models
import sqlite3
from datetime import datetime
from fastapi import Body, Depends, FastAPI, Header, HTTPException, status
from dotenv import load_dotenv
import external_api



app = FastAPI(title="Book Club Library API")

load_dotenv()
API_KEY = os.getenv("API_KEY")


def require_api_key(x_api_key: str | None = Header(default=None)):
    """Reject requests that are missing or have a wrong X-API-Key header."""
    if not API_KEY:
        raise HTTPException(status_code=401, detail="Server API key not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/authors", response_model=list[models.AuthorResponse])
def get_all_authors():
    """Fetch a list of all authors."""
    authors = database.fetch_all_authors()
    return authors


@app.post(
    "/authors",
    status_code=201,
    response_model=models.AuthorResponse,
    dependencies=[Depends(require_api_key)],
)
def create_author(author: models.AuthorCreate):
    """Create a new author."""
    # Pass the validated fields from your AuthorCreate model
    new_author = database.insert_author(
        name=author.name,
        open_library_key=author.open_library_key,
        birth_date=author.birth_date,
        death_date=author.death_date,
    )

    if not new_author:
        raise HTTPException(status_code=400, detail="Failed to create author")

    return new_author


@app.patch(
    "/authors/{author_id}",
    response_model=models.AuthorResponse,
    dependencies=[Depends(require_api_key)],
)
def patch_author(author_id: int, author_update: models.AuthorUpdate):
    """Partially update an author (PATCH)."""
    # exclude_unset=True guarantees we only update fields the client actually provided
    update_data = author_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400, detail="No valid fields provided for update"
        )
    try:
        updated_author = database.update_author(author_id, update_data)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Database constraint failed: Author data already exists",
        )
    if updated_author is None:
        raise HTTPException(
            status_code=404, detail="Author not found or constraint failed"
        )

    return updated_author


@app.put(
    "/authors/{author_id}",
    response_model=models.AuthorResponse,
    dependencies=[Depends(require_api_key)],
)
def put_author(author_id: int, author_update: models.AuthorCreate):
    """Fully replace an author (PUT)."""
    # Exclude unset is omitted to enforce a complete overwrite of all fields
    update_data = author_update.model_dump()
    try:
        updated_author = database.update_author(author_id, update_data)   
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409, 
            detail="Database constraint failed: Author data already exists"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data provided: {str(e)}")
 
    if updated_author is None:
        raise HTTPException(
            status_code=404, detail="Author not found or constraint failed"
        )

    return updated_author


# ---------- Member endpoints ----------


@app.get("/members", response_model=list[models.MemberResponse])
def get_members():
    """Return all members."""
    return database.fetch_all_members()


@app.get("/members/{member_id}", response_model=models.MemberResponse)
def get_one_member(member_id: int):
    """Return one member by id."""
    member = database.fetch_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@app.post("/members", status_code=201, response_model=models.MemberResponse, dependencies=[Depends(require_api_key)])
def create_member(member: models.MemberCreate):
    """Create a new member."""
    try:
        return database.insert_member(member.name, str(member.email), member.phone)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")


@app.patch("/members/{member_id}", response_model=models.MemberResponse, dependencies=[Depends(require_api_key)])
def update_member(member_id: int, member: models.MemberUpdate):
    """Partially update a member. Only provided fields are changed."""
    updates = member.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "email" in updates:
        updates["email"] = str(updates["email"])

    try:
        updated = database.update_member_fields(member_id, updates)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")

    if updated is None:
        raise HTTPException(status_code=404, detail="Member not found")

    return updated


@app.get("/members/{member_id}/loans")
def get_member_loans(member_id: int):
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


# ---------- Loan endpoints ----------


@app.get("/loans", response_model=list[models.LoanResponse])
def get_loans():
    """Return all loans."""
    return database.fetch_all_loans()


@app.get("/loans/{loan_id}", response_model=models.LoanResponse)
def get_one_loan(loan_id: int):
    """Return one loan by id."""
    loan = database.fetch_loan(loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@app.post("/loans", status_code=201, response_model=models.LoanResponse, dependencies=[Depends(require_api_key)])
def create_loan(loan: models.LoanCreate):
    """Create a new loan. Fails if the book is already on an active loan."""
    if database.has_active_loan_for_book(loan.book_id):
        raise HTTPException(status_code=409, detail="Book is already on loan")

    try:
        return database.insert_loan(
            loan.book_id,
            loan.member_id,
            str(loan.loan_date),
            str(loan.due_date),
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid book_id or member_id")


@app.patch("/loans/{loan_id}", response_model=models.LoanResponse, dependencies=[Depends(require_api_key)])
def update_loan(loan_id: int, loan: models.LoanUpdate):
    """Partially update a loan. Use to extend due_date or set return_date."""
    updates = loan.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    for key in ("due_date", "return_date"):
        if key in updates and updates[key] is not None:
            updates[key] = str(updates[key])

    try:
        updated = database.update_loan_fields(loan_id, updates)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid loan data")

    if updated is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    return updated


@app.post("/loans/{loan_id}/return", response_model=models.LoanResponse, dependencies=[Depends(require_api_key)])
def return_book(loan_id: int):
    """Marks a book as returned, unless it already is returned."""
    loan = database.fetch_loan(loan_id)

    # Not found.
    if loan is None:
        raise HTTPException(
            status_code=404, detail="Can't return a loan that does not exist."
        )

    # Conflict.
    if loan["return_date"] is not None:
        raise HTTPException(
            status_code=409,
            detail="Can't return a book that has already been returned.",
        )

    returned_loan = database.return_loan(loan_id)
    return returned_loan


# ---------- Book endpoint talking with external API ----------


@app.get("/get/search")
def search_open_library(isbn: str):
    """Only does a search through the external API."""
    try:
        return external_api.search_books(isbn)

    # Gateway timeout.
    except external_api.OpenLibraryTimeoutError as exception:
        raise HTTPException(status_code=504, detail=str(exception))

    # Bad gateway.
    except external_api.OpenLibraryError as exception:
        raise HTTPException(status_code=502, detail=str(exception))


@app.post("/books/import", response_model=models.BookResponse, status_code=status.HTTP_201_CREATED)
def import_external_book(external_data: models.OpenLibraryBook):
    """Processes raw JSON from Open Library and saves it to the database."""
    data = external_data.model_dump()
    author_ids = []

    names = data.get("author_name", [])
    keys = data.get("author_key", [])

    for i in range(len(names)):
        name = names[i]
        raw_key = keys[i] if i < len(keys) else None

        author_record = database.insert_author(
            name=name, open_library_key=raw_key, birth_date=None, death_date=None
        )
        if author_record:
            author_ids.append(author_record["id"])

    if not author_ids:
        raise HTTPException(
            status_code=400,
            detail="Could not resolve any authors from external payload.",
        )

    # Extract book details and map them to your internal schema

    raw_isbns = data.get("isbn")
    isbn_val = raw_isbns[0] if raw_isbns else None
    raw_subjects = data.get("subject")
    subject_val = ", ".join(raw_subjects) if raw_subjects else ""
    book_data = {
        "title": data.get("title"),
        "isbn": isbn_val,
        "subject": subject_val,
        "first_publish_year": data.get("first_publish_year"),
        "open_library_key": data.get("key"),
        "cover_id": data.get("cover_id"),
    }
    try:
        created_book = database.create_book(book_data, author_ids)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Database constraint failed: This book already exists in the library."
        )   
    if not created_book:
        raise HTTPException(status_code=500, detail="Database insertion failed.")

    return created_book


# ---------- Book endpoints ----------


def find_book(book_id: int):
    """Finds a book by id."""

    book = database.get_book_by_id(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return book

@app.get("/books", response_model=list[models.BookResponse])
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
            status_code=status.HTTP_404_NOT_FOUND, detail="No books found!"
        )

    return books

@app.get("/books/{book_id}", response_model=models.BookResponse)
def get_book(book_id: int):
    """Endpoint for reading a book by id"""

    return find_book(book_id)


@app.post("/books", response_model=models.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: models.BookCreate, author_ids: list[int]= Body(..., description="List of author IDs to link to this book")):
    """Endpoint for adding a new book to the Library."""

    if not book.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and author are required!",
        )

    if not author_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one author ID must be provided!",
        )

    book_data = book.model_dump()

    try:
        created_book = database.create_book(book_data, author_ids)
    except sqlite3.IntegrityError:
        # Triggers if the book ISBN already exists, or if an author_id doesn't exist
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint failed: Book already exists or author ID is invalid.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't save to database!",
        )

    if not created_book:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created book.",
        )

    return created_book


@app.patch(
    "/books/{book_id}",
    response_model=models.BookResponse,
    dependencies=[Depends(require_api_key)],
)
def patch_book(book_id: int, book_update: models.BookUpdate):
    """Partially update a book (PATCH)."""
    # exclude_unset=True guarantees we only update fields the client actually provided
    update_data = book_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400, detail="No valid fields provided for update"
        )
    try:
        updated_book = database.update_book(book_id, update_data)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Database constraint failed: Book data already exists",
        )

    if updated_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return updated_book


@app.delete(
    "/books/{book_id}",
    dependencies=[Depends(require_api_key)],
)
def delete_book(book_id: int):
    try:
        deleted = database.delete_book(book_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Book not found")
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="Database execution failed")

    return {"message": "Book deleted successfully"}
