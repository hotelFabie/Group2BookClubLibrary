"""Book Club Library API."""

from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
import database 
import models


app = FastAPI(title="Book Club Library API")


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Book Club Library API"}

@app.post("/authors", status_code=201, response_model=models.AuthorResponse)
def create_author(author:models.AuthorCreate):
    """Create a new author."""
    # Pass the validated fields from your AuthorCreate model
    new_author = database.insert_author(
        name=author.name,
        open_library_key=author.open_library_key,
        birth_date=author.birth_date,
        death_date=author.death_date
    )
    
    if not new_author:
        raise HTTPException(status_code=400, detail="Failed to create author")
        
    return new_author
