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


def authors_menu():
    pass


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
        elif choice == "3":
            loans_menu()


if __name__ == "__main__":
    main()
