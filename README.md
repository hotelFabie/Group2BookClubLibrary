# Book Club Library (Group 2)

## Description
A terminal based representation of a library, used for book clubs to allow members to search for and borrow books with the program. The data within the scope of the project comes from either manual adding of book data, or retrieval of book data from the **OpenLibrary API**.

Used as a local instance; you as the user executing this have all data stored in a local `.db`-file 

New book data can be retrieved through hich can retrieve book data from OpenLibrary.

## Contributors
Sven, Murtaza, Anastasia & Fabian.

## Getting started
### Dependencies
Data must be run SQLite. 

Python version: 3.14 or later (though anything from 3.10 and onwards should work).

Required modules for successful execution are `fastapi`, `uvicorn`, `pydantic[email]`, `requests` and `python-dotenv`.
(Also specified in `requirements.txt`).

### Execution
To allow fetches to OpenLibrary, first start FastAPI through `uvicorn main:app --reload`, which normally will be started on `127.0.0.1:8000`.
