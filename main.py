"""Book Club Library API."""

import sqlite3
from datetime import datetime

from fastapi import FastAPI, HTTPException

import database
from models import MemberCreate, MemberUpdate, LoanCreate, LoanUpdate


app = FastAPI(title="Book Club Library API")


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Book Club Library API"}


# ---------- Member endpoints ----------


@app.get("/members")
def get_members():
    """Return all members."""
    return database.fetch_all_members()


@app.get("/members/{member_id}")
def get_one_member(member_id: int):
    """Return one member by id."""
    member = database.fetch_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@app.post("/members", status_code=201)
def create_member(member: MemberCreate):
    """Create a new member."""
    try:
        return database.insert_member(member.name, str(member.email), member.phone)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")


@app.patch("/members/{member_id}")
def update_member(member_id: int, member: MemberUpdate):
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


@app.get("/loans")
def get_loans():
    """Return all loans."""
    return database.fetch_all_loans()


@app.get("/loans/{loan_id}")
def get_one_loan(loan_id: int):
    """Return one loan by id."""
    loan = database.fetch_loan(loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@app.post("/loans", status_code=201)
def create_loan(loan: LoanCreate):
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


@app.patch("/loans/{loan_id}")
def update_loan(loan_id: int, loan: LoanUpdate):
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


@app.get("/loans/{loan_id}/return")
def return_book(loan_id: int): 
    """Marks a book as returned, unless it already is returned."""
    loan = database.fetch_loan(loan_id)

    #Not found.
    if loan is None:
        raise HTTPException(status_code=404, detail="Can't return a loan that does not exist.")
    
    #Conflict.
    if loan["return_date"] is not None:    
        raise HTTPException(status_code=409, detail="Can't return a book that has already been returned.")

    returned_loan = database.return_loan(loan_id)
    return returned_loan