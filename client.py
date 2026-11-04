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
        elif choice == "2":
            members_menu()
        elif choice == "3":
            loans_menu()


if __name__ == "__main__":
    main()
