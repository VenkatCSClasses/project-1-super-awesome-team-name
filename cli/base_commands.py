import os
from typing import Annotated
from typer import Typer, Option, Argument, prompt
import requests
from rich import print
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv
from admin_commands import admin
from token_utils import save_token, load_token, delete_token, handle_authorization, get_permissions
from teller_commands import teller
load_dotenv()
server_base_url = os.getenv("SERVER_BASE_URL")

app = Typer(no_args_is_help=True)
app.add_typer(admin, name="admin", help="Admin commands (requires admin permissions)")
app.add_typer(teller, name="teller", help="Teller commands (requires teller or admin permissions)")

permissions = -1

@app.callback()
def main():
    global permissions
    permissions = get_permissions()
    print(permissions)

@app.command()
def register():
    """Register a new user"""
    username = prompt("Enter a username")
    password = prompt(f"Create a password for {username}", hide_input=True, confirmation_prompt=True)
    response = requests.post(f"{server_base_url}/register", json={"username": username, "password": password})
    if response.status_code == 200:
        response_data = response.json()
        print(response_data.get("message", "Registration successful!"))
        token = response_data.get("token")
        save_token(token)
    elif response.status_code == 400:
        print(f"[red]Registration failed: {response.json().get('detail')}[/red]")
    elif response.status_code == 500:
        print("[red]Server error occurred. Please try again later.[/red]")
    else:
        print(f"[red]Registration failed with status code: {response.status_code}[/red]")


@app.command()
def login():
    """Login with username and password"""
    username = prompt("Enter your username")
    password = prompt(f"Password for {username}", hide_input=True)
    response = requests.post(f"{server_base_url}/login", json={"username": username, "password": password})
    if response.status_code == 200:
        response_data = response.json()
        token = response_data["token"]
        save_token(token)
        print(f"[green]{response_data.get('message', 'Login successful!')}[/green]")
    elif response.status_code == 500:
        print("[red]Server error occurred. Please try again later.[/red]")
    else:
        print("[red]Login failed:[/red]", response.json().get("detail"))


@app.command()
def logout():
    """
    Logout the current user
    """
    delete_token()
    print("[green]Logged out successfully![/green]")


@app.command()
def whoami():
    """
    Get the username of the currently logged-in user
    """
    headers, permission = handle_authorization()
    if not headers:
        return
    response = requests.get(f"{server_base_url}/whoami", headers=headers)
    
    if response.status_code == 200:
        print(response.json().get("username", "Unknown user"))
    elif response.status_code == 401:
        print("Unauthorized. Please log in again.")
        delete_token()
    elif response.status_code == 500:
        print("Server error occurred. Please try again later.")
    else:
        print("Response text:", response.text)
        print("Failed to retrieve user info with status code:", response.status_code)


@app.command()
def list_accounts():
    """
    List all accounts for the logged-in user
    """
    headers, permission = handle_authorization()
    if not headers:
        return

    response = {
        "accounts": [
            {"account_id": 1, "account_type": "checking", "balance": 1000.00},
            {"account_id": 2, "account_type": "savings", "balance": 5000.00}
        ]
    }

    table = Table()
    table.add_column("Account ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Account Type", style="magenta")
    table.add_column("Balance", justify="right", style="green")
    for account in response["accounts"]:
        table.add_row(str(account["account_id"]), account["account_type"], f"${account['balance']:.2f}")
    print(table)
    print(f"Total balance: ${sum(account['balance'] for account in response['accounts']):.2f}")


@app.command()
def deposit(account_id: Annotated[int, Argument(help="Account ID to deposit into")], 
            amount: Annotated[float, Argument(help="Amount of money to deposit")]
):
    """Deposit money into an account"""
    headers, permission = handle_authorization()
    if not headers:
        return

    print(f"Depositing ${amount:.2f} to account {account_id}")

    request = {
        "account_id": account_id,
        "amount": amount
    }


@app.command()
def withdraw(account_id: Annotated[int, Argument(help="Account ID to withdraw from")], 
            amount: Annotated[float, Argument(help="Amount of money to withdraw")]
):
    """Withdraw money from an account"""
    headers, permission = handle_authorization()
    if not headers:
        return

    print(f"Withdrawing ${amount:.2f} from account {account_id}")

    request = {
        "account_id": account_id,
        "amount": amount
    }


@app.command()
def transfer(amount: Annotated[float, Argument(help="Amount of money to transfer")], 
             account: Annotated[int, Argument(help="Account ID to transfer from")] = -1, 
             to: Annotated[int, Argument(help="Account ID to transfer to")] = -1
):
    """
    Transfer money between accounts

    [bold cyan]Example:[/bold cyan] 
    [magenta]$[/magenta] transfer 100 --account 1 --to 2
    """
    headers, permission = handle_authorization()
    if not headers:
        return

    print(f"Transferring ${amount:.2f} from account {account} to account {to}")

    request = {
        "from_account_id": account,
        "to_account_id": to,
        "amount": amount
    }