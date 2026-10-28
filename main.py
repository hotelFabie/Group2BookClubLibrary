"""Book Club Library API."""

from fastapi import FastAPI
import database 
import datetime

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
        elif datetime.datetime.strftime(loan["due_date"]) < datetime.datetime.now(): 
            loan["status"] = "Overdue"
        else:
            loan["status"] = "Borrowing"

        loans.append(loan)     
    
    return loans