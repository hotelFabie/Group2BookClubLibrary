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

@app.get("/authors", response_model=list[models.AuthorResponse])
def get_all_authors():
    """Fetch a list of all authors."""
    authors = database.fetch_all_authors()
    return authors

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

@app.patch("/authors/{author_id}", response_model=models.AuthorResponse)
def patch_author(author_id: int, author_update: models.AuthorUpdate):
    """Partially update an author (PATCH)."""
    # exclude_unset=True guarantees we only update fields the client actually provided
    update_data = author_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")
        
    updated_author = database.update_author(author_id, update_data)
    
    if updated_author is None:
        raise HTTPException(status_code=404, detail="Author not found or constraint failed")
        
    return updated_author

@app.put("/authors/{author_id}", response_model=models.AuthorResponse)
def put_author(author_id: int, author_update: models.AuthorCreate):
    """Fully replace an author (PUT)."""
    # Exclude unset is omitted to enforce a complete overwrite of all fields
    update_data = author_update.model_dump()
    
    updated_author = database.update_author(author_id, update_data)
    
    if updated_author is None:
        raise HTTPException(status_code=404, detail="Author not found or constraint failed")
        
    return updated_author
