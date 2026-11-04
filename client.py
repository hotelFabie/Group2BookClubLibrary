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
    pass


def members_menu():
    pass


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
            print(f"ID: {author['id']}, Name: {author['name']}, Birth Date: {author.get('birth_date')}, Death Date: {author.get('death_date')}")
    
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
        "death_date": death_date if death_date else None
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
    birth_date = input("Enter the new birth date (YYYY-MM-DD, leave blank to keep current): ").strip()
    death_date = input("Enter the new death date (YYYY-MM-DD, leave blank to keep current): ").strip()

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
        response = requests.patch(f"{API_BASE_URL}/authors/{author_id}", json=data, timeout=5)
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
            return
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
