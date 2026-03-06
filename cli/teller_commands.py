from typer import Typer, prompt, confirm
import requests
from dotenv import load_dotenv
import os
load_dotenv()
server_base_url = os.getenv("SERVER_BASE_URL")

teller = Typer(no_args_is_help=True)

@teller.command()
def create_account(customer_username: str, initial_deposit: float = 0.0):
    """Create a new bank account for a customer with an optional initial deposit"""
    pass

@teller.command()
def close_account(account_id: int):
    """Close an existing bank account"""
    pass

@teller.command()
def view_accounts(customer_username: str):
    """View all accounts for a specific customer"""
    pass


@teller.command()
def create_user():
    """Create a new user (customer or teller)"""
    username =  prompt("Enter a username")
    password = prompt(f"Enter password for {username}", hide_input=True, confirmation_prompt=True)

    is_teller = confirm("Should this user be a teller?", default=False)

    permission_level = AccountType.customer.value
    if is_teller:
        permission_level = AccountType.teller.value

    response = requests.post(
        f"{server_base_url}/create_user", 
        json={
            "username": username, 
            "password": password, 
            "permission": permission_level
        }
    )
    # if response.status_code == 201:
    #     print(response.json().get("message", "User created successfully!"))
    # elif response.status_code == 400:
    #     print("Bad request:", response.json().get("detail", "Unknown error"))
    # elif response.status_code == 500:
    #     print("Server error occurred. Please try again later.")
    # else:
    #     print("Response text:", response.text)
    #     print("Failed to create user with status code:", response.status_code)