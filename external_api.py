#Assisting method for a GET endpoint for Books.
#This is for fetching new results from outside of our local "library".

import requests

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

class OpenLibraryError(Exception):
    """There are many possible errors that can arise, so this one covers most that can happen."""
    pass

class OpenLibraryTimeoutError(Exception):
    """Having a specific error for timeout, as it is more easily detected."""
    pass

def search_books(isbn : str) -> dict:
    """
    Searches for books on Open Library using an ISBN, 
    resulting in a JSON response if the fetch succeeds.
    """

    try:
        response = requests.get(
            OPEN_LIBRARY_URL,
            params = {
                "isbn" : isbn,
                "fields" : "title,key,isbn,cover_i,subject,author_name,author_key"
            },
            timeout = 10
        )
        
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exception:
        raise OpenLibraryError("Exception: Data retrieval from from OpenLibrary failed.") from exception

    except requests.exceptions.Timeout as exception:
        raise OpenLibraryTimeoutError("Timeout on request to OpenLibrary.") from exception