#Assisting method for a GET endpoint for Books.
#This is for fetching new results from outside of our local "library".

import requests

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

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
                "fields" : "title,key,isbn,cover_i,subject"
            },
            timeout = 10
        )
        
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