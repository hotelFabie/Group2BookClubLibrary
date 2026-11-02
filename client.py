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


def books_menu():
    pass


def members_menu():
    pass


def loans_menu():
    print("\n--- Loans ---")
    print("1. List all loans")
    print("2. List loans for a member")
    print("3. Extend a loan")
    print("0. Back to main menu")

    choice = input("Choose an option: ").strip()

    if choice == "0":
        return


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
