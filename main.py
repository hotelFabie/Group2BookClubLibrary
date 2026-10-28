"""Book Club Library API."""

from fastapi import FastAPI


app = FastAPI(title="Book Club Library API")


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Book Club Library API"}

#Delete later, when I am done.
from database import get_connection

#I do not think we need to return everything as a loan.
@app.get("/members/{member_id}/loans")
def get_member_loans(member_id : int):
    "Shows status on all loans per members."
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM loans WHERE member_id = ?", (member_id,)
        ).fetchall()
    finally:
        conn.close().fetchall()

    loans = []

    for loan in rows:
        match loan["status"]:
            case:
                #Insertion into loans.
    #We probably need to give a status indicator on our own here... 
    return loans

#Have to take care of the possibility of there not being any loans