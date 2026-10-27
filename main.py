"""Book Club Library API."""

from fastapi import FastAPI


app = FastAPI(title="Book Club Library API")


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Book Club Library API"}
