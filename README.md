# Book Club Library (Group 2)

## Description
A terminal based representation of a library, used for book clubs to allow members to search for and borrow books with the program. The data within the scope of the project comes from either manual adding of book data, or retrieval of book data from the **OpenLibrary API**.

Used as a local instance; you as the user executing this have all data stored in a local `.db`-file through SQLite.  

Both local and external API data is dealt with through FastAPI.

## Contributors
Sven, Murtaza, Anastasia & Fabian.

## Getting started
### Dependencies
SQLite. 

Python version: 3.14 or later (though anything from 3.10 and onwards should work).

Required modules for successful execution are `fastapi`, `uvicorn`, `pydantic[email]`, `requests` and `python-dotenv`.
(Also specified in `requirements.txt`).

### Execution
#### Preparation
Database can be seeded with base data from `seed.py`, which will generate a `library.db` database file.

To allow fetches to OpenLibrary, first start FastAPI through `uvicorn main:app --reload`, which normally will be started on `127.0.0.1:8000`.

### Run the main program
Start the client with `python client.py` within the same directory as the project. Then, feel free to choose any menu alternative that comes up in the terminal after running the command.