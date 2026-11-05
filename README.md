# Book Club Library (Group 2)

## Description
A terminal based representation of a library, used for book clubs to allow members to search for and borrow books with the program. The data within the scope of the project comes from either manual adding of book data, or retrieval of book data from the **OpenLibrary API**.

Used as a local instance; you as the user executing this have all books (and their data) data stored in a local `.db`-file through SQLite.  

Data transmission from the external API is done by retrieving a JSON response with book data, and all data then dealt with locally is done through endpoints we've set up with FastAPI. The endpoints that are so far protected by API key authentication are the POST methods (for creating resources). 

## Contributors
Sven, Murtaza, Anastasia & Fabian.

## Getting started
### Dependencies
SQLite. 

Python versions from 3.10 and later should work.

Required packages - `fastapi`, `uvicorn`, `pydantic[email]`, `requests` and `python-dotenv` - exist in `requirements.txt`, and
can be downloaded as `pip install -r requirements.txt`.

### Execution
#### Preparation
For POST methods to go through, setup a local `.env` file, following the `.env.example` file as an example.
This means that you as a team need to use e.g. a trustworthy API key generator, so everyone that should be able to POST has a unique key allowing them to make changes.

Database can be seeded with base/sample data from `seed.py`, which will generate a `library.db` database file.

To allow fetches to OpenLibrary, first start FastAPI through `uvicorn main:app --reload`, which normally will be started on `127.0.0.1:8000`.

### Run the main program
Start the client with `python client.py` within the same directory as the project. Then, feel free to choose any menu alternative that comes up in the terminal after running the command.