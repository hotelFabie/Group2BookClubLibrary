import json
import os
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


def get_json(url, params=None, headers=None, timeout=5):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("The request took too long")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
    except requests.exceptions.HTTPError as error:
        print(f"The server said no: {error.response.status_code}")
    except requests.exceptions.JSONDecodeError:
        print("The answer was not JSON")
    except requests.exceptions.RequestException as error:
        print(f"Someting else went wrong: {type(error).__name__}")
    return None


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
            f"{API_BASE_URL}/books/get", 
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
    # Fetch all books and find the ID client-side
    try:
        response = requests.get(f"{API_BASE_URL}/books", timeout=5)
        response.raise_for_status()
        all_books = response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching books: {e}")
        return
    matches = [b for b in all_books if b["title"].lower() == book_title.lower()]
    print(matches)
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
        book_id = input("Enter the ID you want to update: ").strip()

    new_title = input("Insert New Title, or leave blank to keep current: ").strip()
    new_publish_year = input("Insert New First Publish Year, or leave blank to keep current: ").strip()
    new_open_library_key = input("Insert New Open Library Key, or leave blank to keep current: ").strip()
    new_cover_id = input("Insert New Cover ID, or leave blank to keep current: ").strip()
    new_isbn = input("Insert New ISBN, or leave blank to keep current: ").strip()
    new_subject = input("Insert New Subject, or leave blank to keep current: ").strip()

    update_data = {}
    if new_title:
        update_data["title"] = new_title

    if new_publish_year:
        update_data["first_publish_year"] = new_publish_year

    if new_open_library_key:
        update_data["open_library_key"] = new_open_library_key

    if new_cover_id:
        update_data["cover_id"] = new_cover_id

    if new_isbn:
        update_data["isbn"] = new_isbn

    if new_subject:
        update_data["subject"] = new_subject

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
    # Fetch all books and find the ID client-side
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
    while True:
        print("\n--- Members ---")
        print("1. List all members")
        print("2. Get one member")
        print("3. Create a new member")
        print("4. Update a member")
        print("0. Back to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return
        elif choice == "1":
            list_all_members()
        elif choice == "2":
            get_one_member()
        elif choice == "3":
            create_member()
        elif choice == "4":
            update_member()


def list_all_members():
    try:
        response = requests.get(f"{API_BASE_URL}/members")
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("Could not reach the API. Is the server running?")
        return
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e}")
        return

    members = response.json()
    print(json.dumps(members, indent=2))


def get_one_member():
    member_id = input("Member id: ").strip()

    try:
        response = requests.get(f"{API_BASE_URL}/members/{member_id}")
    except requests.exceptions.ConnectionError:
        print("Could not reach the API. Is the server running?")
        return

    if response.status_code == 404:
        print("Member not found.")
        return

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e}")
        return

    member = response.json()
    print(json.dumps(member, indent=2))


def create_member():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()

    payload = {"name": name, "email": email}
    if phone:
        payload["phone"] = phone

    try:
        response = requests.post(f"{API_BASE_URL}/members", json=payload)
    except requests.exceptions.ConnectionError:
        print("Could not reach the API. Is the server running?")
        return

    if response.status_code == 409:
        print("A member with that email already exists.")
        return

    if response.status_code == 422:
        print("Invalid data. Check that email is in a valid format.")
        return

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e}")
        return

    member = response.json()
    print("Member created:")
    print(json.dumps(member, indent=2))


def update_member():
    member_id = input("Member id: ").strip()

    print("Leave a field blank to skip it.")
    name = input("New name: ").strip()
    email = input("New email: ").strip()
    phone = input("New phone: ").strip()

    payload = {}
    if name:
        payload["name"] = name
    if email:
        payload["email"] = email
    if phone:
        payload["phone"] = phone

    if not payload:
        print("Nothing to update.")
        return

    try:
        response = requests.patch(
            f"{API_BASE_URL}/members/{member_id}",
            json=payload,
        )
    except requests.exceptions.ConnectionError:
        print("Could not reach the API. Is the server running?")
        return

    if response.status_code == 404:
        print("Member not found.")
        return

    if response.status_code == 409:
        print("A member with that email already exists.")
        return

    if response.status_code == 422:
        print("Invalid data.")
        return

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e}")
        return

    member = response.json()
    print("Member updated:")
    print(json.dumps(member, indent=2))


def list_all_loans():
    try:
        response = requests.get(f"{API_BASE_URL}/loans")
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("Could not reach the API. Is the server running?")
        return
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e}")
        return

    loans = response.json()
    print(json.dumps(loans, indent=2))


def extend_loan():
    loan_id = input("Loan id: ").strip()
    new_due_date = input("New due date (YYYY-MM-DD): ").strip()
    response = requests.patch(
        f"{API_BASE_URL}/loans/{loan_id}",
        json={"due_date": new_due_date},
    )

    if response.status_code == 404:
        print("Loan not found.")
        return

    response.raise_for_status()
    loan = response.json()
    print(json.dumps(loan, indent=2))


def loans_menu():
    while True:
        print("\n--- Loans ---")
        print("1. List all loans")
        print("2. List loans for a member")
        print("3. Extend a loan")
        print("0. Back to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return
        elif choice == "1":
            list_all_loans()
        elif choice == "2":
            list_member_loans()
        elif choice == "3":
            extend_loan()


def list_member_loans():
    member_id = input("Member id: ").strip()
    response = requests.get(f"{API_BASE_URL}/members/{member_id}/loans")
    response.raise_for_status()
    loans = response.json()

    if not loans:
        print("No loans found for this member.")
        return

    print(json.dumps(loans, indent=2))


# ----------- Authors menu section --------------


def authors_menu():
    """Generate authors menu"""

    while True:
        print("\n--- Authors Menu ---")
        print("1. List all authors")
        print("2. Add a new author")
        print("3. Update an existing author")
        print("0. Back to main menu")

        user_choice = input("Choose an option: ").strip()

        if user_choice == "0":
            return
        elif user_choice == "1":
            list_all_authors()
        elif user_choice == "2":
            add_new_author()
        elif user_choice == "3":
            update_existing_author()
        elif user_choice == "0":
            return


def list_all_authors():
    """Fetch and display all authors from the API."""
    try:
        authors = get_json(f"{API_BASE_URL}/authors", timeout=5)

        if not authors:
            return

        print("\n--- List of Authors ---")
        for author in authors:
            print(
                f"ID: {author['id']}, Name: {author['name']}, Birth Date: {author.get('birth_date')}, Death Date: {author.get('death_date')}"
            )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching authors: {e}")


def add_new_author():
    """Add a new author to the API."""
    name = input("Enter the author's name: ").strip()
    birth_date = input("Enter the author's birth date (YYYY-MM-DD): ").strip()
    death_date = input("Enter the author's death date (YYYY-MM-DD, optional): ").strip()

    if not name:
        print("Author name is required.")
        return

    data = {
        "name": name,
        "birth_date": birth_date if birth_date else None,
        "death_date": death_date if death_date else None,
    }

    try:
        response = requests.post(f"{API_BASE_URL}/authors", json=data, timeout=5)
        response.raise_for_status()
        print("Author added successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error adding author: {e}")


def update_existing_author():
    """Update an existing author in the API."""
    author_id = input("Enter the ID of the author to update: ").strip()
    name = input("Enter the new name (leave blank to keep current): ").strip()
    birth_date = input(
        "Enter the new birth date (YYYY-MM-DD, leave blank to keep current): "
    ).strip()
    death_date = input(
        "Enter the new death date (YYYY-MM-DD, leave blank to keep current): "
    ).strip()

    if not author_id.isdigit():
        print("Invalid author ID.")
        return

    data = {}
    if name:
        data["name"] = name
    if birth_date:
        data["birth_date"] = birth_date
    if death_date:
        data["death_date"] = death_date

    if not data:
        print("No updates provided.")
        return

    try:
        response = requests.patch(
            f"{API_BASE_URL}/authors/{author_id}", json=data, timeout=5
        )
        response.raise_for_status()
        print("Author updated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error updating author: {e}")


def filter_by_author():
    pass


def main():
    while True:
        print("\n--- Book Club Library ---")
        print("1. Books")
        print("2. Members")
        print("3. Loans")
        print("4. Authors")
        print("0. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            books_menu()
        elif choice == "2":
            members_menu()
        elif choice == "3":
            loans_menu()
        elif choice == "4":
            authors_menu()


if __name__ == "__main__":
    main()
