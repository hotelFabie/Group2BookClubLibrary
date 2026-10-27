import requests

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def search_books(title : str, limit : int = 5) -> dict:
    """
        Finds books all books matching the specified title, 
        with the result being limited to 5, 
        or what number is being specified as an argument. 
        Returns the response in JSON format.
    """

    response = requests.get(
        OPEN_LIBRARY_URL,
        params={
            "title" : title,
            "limit" : limit
        }
    )

    return response.json()