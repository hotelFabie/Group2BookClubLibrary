from datetime import datetime
from pydantic import BaseModel

#Books
class Book(BaseModel):
    id : int
    title: str
    first_publish_year: int | None = None
    open_library_key: str | None = None
    cover_id: int | None = None
    isbn: str | None = None
    subject: str | None = None

#Authors
class Author(BaseModel):
    id : int
    name : str
    open_library_key | None = None
    birth_date : datetime | None = None #Or date
    death_date : datetime | None = None #Or date

#Members
class Member(BaseModel):
 id : int
 name : str
 email : str
 phone : str | None = None
 joined_date : datetime #Or date

#Loans
class Loan(BaseModel):
    id : int    
    #