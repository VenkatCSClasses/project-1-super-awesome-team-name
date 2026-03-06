import os
from typing import Annotated
from typer import Typer, Argument, prompt
import requests
from rich import print
from rich.table import Table
from dotenv import load_dotenv
from admin_commands import admin
from token_utils import save_token, delete_token, handle_authorization, get_permissions
from teller_commands import teller
load_dotenv()
server_base_url = os.getenv("SERVER_BASE_URL")


permissions = get_permissions()

app = Typer(no_args_is_help=True)
app.add_typer(admin, name="admin", help="Admin commands (requires admin permissions)", hidden=permissions < 2)
app.add_typer(teller, name="teller", help="Teller commands (requires teller or admin permissions)", hidden=permissions < 1)



@app.callback()
def main():
    pass

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


@app.command(hidden=permissions < 0)
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


@app.command(hidden=permissions < 0)
def list_accounts():
    """
    List all accounts for the logged-in user
    """
    headers, permission = handle_authorization()
    if not headers:
        return

    response = requests.get(f"{server_base_url}/bank/get_all_bank_accounts", headers=headers)
    if response.status_code == 200:
        response_data = response.json()
    elif response.status_code == 401:
        print("Unauthorized. Please log in again.")
        delete_token()
        return
    elif response.status_code == 500:
        print("Server error occurred. Please try again later.")
        return
    else:
        print("Response text:", response.text)
        print("Failed to retrieve accounts with status code:", response.status_code)
        return


    table = Table()
    table.add_column("Account ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Account Type", style="magenta")
    table.add_column("Balance", justify="right", style="green")
    for account in response_data["accounts"]:
        table.add_row(str(account["account_id"]), account["account_type"], f"${account['balance']:.2f}")
    print(table)
    print(f"Total balance: ${sum(account['balance'] for account in response_data['accounts']):.2f}")


@app.command(hidden=permissions < 0)
def deposit(account_id: Annotated[int, Argument(help="Account ID to deposit into")], 
            amount: Annotated[float, Argument(help="Amount of money to deposit")]
):
    """Deposit money into an account"""
    headers, permission = handle_authorization()
    if not headers:
        return

    response = requests.post(f"{server_base_url}/bank/deposit", json={"account_id": account_id, "amount": amount}, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data.get("message", f"Deposit successful! Balance is now ${response_data.get('balance', 'unknown')}"))
    elif response.status_code == 400:
        print(f"[red]Deposit failed: {response.json().get('detail')}[/red]")
    elif response.status_code == 500:
        print("[red]Server error occurred. Please try again later.[/red]")
    else:
        print(f"[red]Deposit failed with status code: {response.status_code}[/red]")

    
@app.command(hidden=permissions < 0)
def withdraw(account_id: Annotated[int, Argument(help="Account ID to withdraw from")], 
            amount: Annotated[float, Argument(help="Amount of money to withdraw")]
):
    """Withdraw money from an account"""
    headers, permission = handle_authorization()
    if not headers:
        return

    response = requests.post(f"{server_base_url}/bank/withdraw", json={"account_id": account_id, "amount": amount}, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data.get("message", f"Withdrawal successful! Balance is now ${response_data.get('balance', 'unknown')}"))
    elif response.status_code == 400:
        print(f"[red]Withdrawal failed: {response.json().get('detail')}[/red]")
    elif response.status_code == 500:
        print("[red]Server error occurred. Please try again later.[/red]")
    else:
        print(f"[red]Withdrawal failed with status code: {response.status_code}[/red]")


@app.command(hidden=permissions < 0)
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

    response = requests.post(f"{server_base_url}/bank/transfer", json={"from_account_id": account, "to_account_id": to, "amount": amount}, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data.get("message", f"Transfer successful! Balance is now ${response_data.get('balance', 'unknown')}"))
    elif response.status_code == 400:
        print(f"[red]Transfer failed: {response.json().get('detail')}[/red]")
    elif response.status_code == 500:
        print("[red]Server error occurred. Please try again later.[/red]")
    else:
        print(f"[red]Transfer failed with status code: {response.status_code}[/red]")


@app.command()
def open_account(account_type: Annotated[str, Argument(help="Type of account to open (checking or savings)")] = "checking"):
    """Open a new bank account"""
    headers, permission = handle_authorization()
    if not headers:
        return
    if account_type not in ["checking", "savings"]:
        print("[red]Invalid account type. Please choose 'checking' or 'savings'.[/red]")
        return

    response = requests.post(f"{server_base_url}/bank/create_bank_account", json={"bank_account_type": account_type}, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data.get("message", f"{account_type.capitalize()} account created successfully! Account ID: {response_data.get('account_id', 'unknown')}"))
    elif response.status_code == 400:
        print(f"[red]Account creation failed: {response.json().get('detail')}[/red]")
    elif response.status_code == 500:
        print("[red]Server error occurred. Please try again later.[/red]")
    else:
        print(f"[red]Account creation failed with status code: {response.status_code}[/red]")