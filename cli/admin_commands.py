from typer import Typer, Option, confirm, Argument, prompt
from enum import Enum
from typing import Annotated
import requests
from dotenv import load_dotenv
import os
from token_utils import handle_authorization
load_dotenv()
server_base_url = os.getenv("SERVER_BASE_URL")

admin = Typer(no_args_is_help=True)

class AccountType(str, Enum):
    customer = 0
    teller = 1 
    admin = 2 # Highest permission level


@admin.command()
def create_user():
    headers, permission = handle_authorization()
    if not headers:
        return
    """Create a new user (customer, teller, or admin)"""
    username =  prompt("Enter a username")
    password = prompt(f"Enter password for {username}", hide_input=True, confirmation_prompt=True)

    is_teller = confirm("Should this user be a teller?", default=False)

    permission_level = AccountType.customer.value
    if is_teller:
        permission_level = AccountType.teller.value
        is_admin = confirm("Should this user be an admin?", default=False)
    
        permission_level = AccountType.admin.value if is_admin else AccountType.teller.value

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


@admin.command()
def delete_user(username: Annotated[str, Argument(help="Username of the user to delete")]):
    headers, permission = handle_authorization()
    if not headers:
        return
    """Delete an existing user by username"""
    pass
    # response = requests.delete(f"{server_base_url}/delete_user/{username}")
    # if response.status_code == 200:
    #     print(response.json().get("message", "User deleted successfully!"))
    # elif response.status_code == 404:
    #     print("User not found:", response.json().get("detail", "Unknown error"))
    # elif response.status_code == 500:
    #     print("Server error occurred. Please try again later.")
    # else:
    #     print("Response text:", response.text)
    #     print("Failed to delete user with status code:", response.status_code)


@admin.command()
def get_total_balance():
    headers, permission = handle_authorization()
    if not headers:
        return
    """Get the total balance across all accounts in the system"""
    pass
    # headers = handle_authorization()
    # if not headers:
    #     return
    
    # response = requests.get(f"{server_base_url}/total_balance", headers=headers)
    # if response.status_code == 200:
    #     total_balance = response.json().get("total_balance")
    #     print(f"Total balance across all accounts: ${total_balance:.2f}")
    # elif response.status_code == 403:
    #     print("Unauthorized: You do not have permission to perform this action.")
    # elif response.status_code == 500:
    #     print("Server error occurred. Please try again later.")
    # else:
    #     print("Response text:", response.text)
    #     print("Failed to retrieve total balance with status code:", response.status_code)