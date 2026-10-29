"""Book Club Library API."""

import sqlite3
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

import database


app = FastAPI(title="Book Club Library API")


class MemberCreate(BaseModel):
    """Payload for creating a member."""

    name: str
    email: EmailStr
    phone: str | None = None


class MemberUpdate(BaseModel):
    """Payload for partially updating a member. All fields optional."""

    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Book Club Library API"}


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

    # EmailStr → str för SQLite
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

#We will need to implement the methods within database.py

@app.get("/loans/{loan_id}/return")
def return_book(loan_id: int): 
    #Pre database execution check.
    #This may not be the correct method name; check with responsible.
    loan = database.fetch_one_loan(loan_id)

    #Unless the method above has some solution for it:
    if loan is None:
        #Not found.
        raise HTTPException(status_code=404, detail="Can't return a loan that does not exist.")

    if loan["return_date"] is not None:
        #Conflict.
        raise HTTPException(status_code=409, detail="Can't return a book that has already been returned.")

    returned_loan = database.return_loan(loan_id)
    return returned_loan