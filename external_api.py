#Assisting method for our GET endpoint for books.

import requests

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def search_books(title : str, limit : int = 5) -> dict:
    """
    Searches for books based on title and limit (5 unless specified), 
    with result in JSON if the fetch is successful.
    """

    try:
        response = requests.get(
        OPEN_LIBRARY_URL,
        params = {
            "title" : title,
            "limit" : limit,
            "fields" : "title,key,isbn,cover_i,subject"
        },
        timeout = 10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Exception: Timeout on request to OpenLibrary.")
    except requests.exceptions.ConnectionError:
        print("Exception: Connection to OpenLibrary failed.")
    except requests.exceptions.HTTPError as http_error:
        print(f"Exception: HTTP error from OpenLibrary with the status code: {http_error.response.status_code}")
    except requests.exceptions.RequestException as other_error:
        print(f"Exception: Fetch from OpenLibrary resulted in {other_error}.")