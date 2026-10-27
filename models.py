from datetime import date
from pydantic import BaseModel

# Book Models
class BookBase(BaseModel):
    title: str
    first_publish_year: int | None = None
    open_library_key: str | None = None
    cover_id: int | None = None
    isbn: str | None = None
    subject: str | None = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int

# Author Models
class AuthorBase(BaseModel):
    name: str
    open_library_key: str | None = None
    birth_date: date | None = None
    death_date: date | None = None

class AuthorCreate(AuthorBase):
    pass

class AuthorResponse(AuthorBase):
    id: int

# Member Models
class MemberBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    joined_date: date

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int


# Loan Models
class LoanBase(BaseModel):
    book_id: int
    member_id: int
    loan_date: date
    due_date: date
    returned_date: date | None = None

class LoanCreate(LoanBase):
    pass

class LoanResponse(LoanBase):
    id: int
 