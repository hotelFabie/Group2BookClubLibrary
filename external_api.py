import requests

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def search_books(title : str, limit : int = 5) -> dict:
    """
        Searches for books in Open Library which match on the specified title, 
        with the result being limited to 5, 
        or what number is being specified as an argument. 
        Returns the response in JSON format.
    """

    response = requests.get(
        OPEN_LIBRARY_URL,
        params = {
            "title" : title,
            "limit" : limit,
            "fields" : "title,key,isbn,cover_i,subject"
        },
        timeout = 10
    )

    response.raise_for_status()

    #This may give way more than we actually need.
    return response.json()

#It is worth testing this by applying it into the actual GET that is used.