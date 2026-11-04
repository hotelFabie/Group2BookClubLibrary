import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"
API_KEY = os.getenv("API_KEY")


def check_api_is_up() -> bool:
    """Ping the API root. Return True if it answers, False if not."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False

#Ana
def books_menu():
    """Generate the books menu loop."""
    while True:
        print("\n--- Books Menu ---")
        print("1. Find books by id")
        print("2. Find books by author")
        print("3. Add a new book manually")
        print("4. Add a new book from Open Library")
        print("5. Update a book")
        print("6. Delete a book")
        print("0. Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            find_books_by_id()
        elif choice == "2":
            find_books_by_author()
        elif choice == "3":
            add_book_manual()
        elif choice == "4":
            add_book_external()
        elif choice == "5":
            update_book()
        elif choice == "6":
            delete_book()
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")

def find_books_by_id():
    """Collect data and send a GET request to find a book by ID."""
    book_id = input("Enter book ID: ").strip()
    
    if not book_id.isdigit():
        print("Invalid input: Book ID must be a number.")
        return

    try:
        response = requests.get(f"{API_BASE_URL}/books/{book_id}", timeout=5)
        response.raise_for_status()
        book = response.json()
        print(f"Book found: {book}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to find book: {e}")

def find_books_by_author():
    """Collect data and send a GET request to find books by author ID."""
    author_id = input("Enter author ID: ").strip()
    
    if not author_id.isdigit():
        print("Invalid input: Author ID must be a number.")
        return

    try:
        response = requests.get(f"{API_BASE_URL}/books", params={"author": author_id}, timeout=5)
        response.raise_for_status()
        books = response.json()
        print(f"Books found: {books}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to find books by author: {e}")


def add_book_manual():
    """Collect data and send a POST request to create a book."""
    title = input("Enter book title: ").strip()
    
    if not title:
        print("Title is required.")
        return
        
    author_names_str = input("Enter author names (comma-separated): ").strip()
    if not author_names_str:
        print("At least one author is required.")
        return

    author_names = [name.strip() for name in author_names_str.split(",") if name.strip()]
    author_ids = []
    
    #  Finds or creates authors and collects their IDs
    for name in author_names:
        try:
            # Send name to the Get-or-Create endpoint
            author_data = {"name": name}
            response = requests.post(f"{API_BASE_URL}/authors", json=author_data, timeout=5)
            response.raise_for_status()
            
            # Extract the ID from the returned JSON
            author = response.json()
            author_ids.append(author["id"])
        except requests.exceptions.RequestException as e:
            print(f"Failed to process author '{name}': {e}")
            return # Abort the whole book creation if an author fails

    payload = {
        "book": {"title": title},
        "author_ids": author_ids
    }

    try:
        response = requests.post(f"{API_BASE_URL}/books", json=payload, timeout=5)
        response.raise_for_status()
        print("Book and authors linked successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to add book: {e}")

def add_book_external():

    """Ask for an ISBN, fetch from the backend, and display the result."""
    isbn = input("Enter the ISBN to search Open Library: ").strip()
    
    if not isbn:
        print("ISBN is required.")
        return

    try:
        response = requests.get(
            f"{API_BASE_URL}/books/get/search", 
            params={"isbn": isbn}, 
            timeout=10
        )
        
        if response.status_code == 404:
            print("Book not found on Open Library.")
            return
        elif response.status_code != 200:
            print(f"Backend returned an error: {response.status_code}")
            return
            
        book_data = response.json()
        
        docs = book_data.get("docs", [])
        if not docs:
            print("No matching books found in the external data.")
            return
            
        book = docs[0]
        title = book.get("title", "Unknown Title")
        authors = ", ".join(book.get("author_name", ["Unknown Author"]))
        
        print(f"\nFound: '{title}' by {authors}")
        
        confirm = input("\nWould you like to import this book into the library? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("Import cancelled.")
            return

        try:
            # Send the specific Open Library document dictionary to the database
            import_response = requests.post(
                f"{API_BASE_URL}/books/import", 
                json=book, 
                timeout=5
            )
            import_response.raise_for_status()
            print("Book and authors successfully imported into the database!")
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to import the book: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Could not connect to the local backend: {e}")

def update_book():
    book_title = input("Enter the title of the book to update: ").strip()
    if not book_title:
        print("Book title is required.")
        return  
    # 1. Fetch all books and find the ID client-side
    try:
        response = requests.get(f"{API_BASE_URL}/books", timeout=5)
        response.raise_for_status()
        all_books = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching books: {e}")
        return
    matches = [b for b in all_books if b["title"].lower() == book_title.lower()]
    if not matches:
        print("No book found with that title.")
        return
    if len(matches) == 1:
        book_id = matches[0]["id"]
        print(f"Found '{matches[0]['title']}'. (ID: {book_id})")
    else:
        print("Multiple matches found:")
        for b in matches:
            print(f"ID: {b['id']} | Title: {b['title']}")
        book_id = input("Enter the exact ID you want to update: ").strip()

    print("\nEnter book id (leave blank to keep current):")
    new_title = input("New title: ").strip()
    
    update_data = {}
    if new_title:
        update_data["title"] = new_title

    if not update_data:
        print("No changes provided.")
        return

    try:
        patch_response = requests.patch(f"{API_BASE_URL}/books/{book_id}", json=update_data, timeout=5)
        patch_response.raise_for_status()
        print("Book updated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error updating book: {e}")
    
def delete_book():
    book_title = input("Enter the title of the book to delete: ").strip()
    if not book_title:
        print("Book title is required.")
        return  
    # 1. Fetch all books and find the ID client-side
    try:
        response = requests.get(f"{API_BASE_URL}/books", timeout=5)
        response.raise_for_status()
        all_books = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching books: {e}")
        return
    matches = [b for b in all_books if b["title"].lower() == book_title.lower()]
    if not matches:
        print("No book found with that title.")
        return
    if len(matches) == 1:
        book_id = matches[0]["id"]
        print(f"Found '{matches[0]['title']}'. (ID: {book_id})")
    else:
        print("Multiple matches found:")
        for b in matches:
            print(f"ID: {b['id']} | Title: {b['title']}")
        book_id = input("Enter the exact ID you want to delete: ").strip()

    confirm = input(f"Are you sure you want to delete the book with ID {book_id}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.")
        return

    try:
        delete_response = requests.delete(f"{API_BASE_URL}/books/{book_id}", timeout=5)
        delete_response.raise_for_status()
        print("Book deleted successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error deleting book: {e}")  
    
def members_menu():
    pass


def loans_menu():
    pass


def authors_menu():
    pass


def filter_by_author():
    pass


def main():
    """Show the menu and read one choice."""
    print("\n--- Book Club Library ---")
    print("1. Books")
    print("2. Members")
    print("3. Loans")
    print("4. Authors")
    print("0. Quit")

    choice = input("Choose an option: ").strip()

    if choice == "0":
        return


if __name__ == "__main__":
    main()
