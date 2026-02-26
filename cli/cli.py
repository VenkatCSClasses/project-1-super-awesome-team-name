import os
from typer import Typer, Option
import requests
from dotenv import load_dotenv
from token_utils import save_token, load_token, delete_token
load_dotenv()
server_base_url = os.getenv("SERVER_BASE_URL")

app = Typer(no_args_is_help=True)


@app.callback()
def main():
    pass

@app.command()
def register(username: str, password: str = Option(prompt="Create a password", hide_input=True, confirmation_prompt=True)):
    response = requests.post(f"{server_base_url}/register", json={"username": username, "password": password})
    if response.status_code == 200:
        response_data = response.json()
        print(response_data.get("message", "Registration successful!"))
        token = response_data.get("token")
        save_token(token)
    elif response.status_code == 400:
        print("Registration failed, user already exists:", response.json().get("detail"))
    elif response.status_code == 500:
        print("Server error occurred. Please try again later.")
    else:
        print("Response text:", response.text)
        print("Registration failed with status code:", response.status_code)


@app.command()
def login(username: str, password: str = Option(prompt="Enter password", hide_input=True)):
    response = requests.post(f"{server_base_url}/login", json={"username": username, "password": password})
    if response.status_code == 200:
        response_data = response.json()
        token = response_data["token"]
        save_token(token)
        print(response_data.get("message", "Login successful!"))
    elif response.status_code == 500:
        print("Server error occurred. Please try again later.")
    else:
        print("Response text:", response.text)
        print("Login failed:", response.json().get("detail"))


@app.command()
def logout():
    delete_token()
    print("Logged out successfully!")


def handle_authorization():
    token = load_token()
    if not token:
        print("You must be logged in to perform this action.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    return headers

@app.command()
def protected_action():
    headers = handle_authorization()
    if not headers:
        return
    response = requests.get(f"{server_base_url}/protected", headers=headers)
    
    if response.status_code == 200:
        print(response.json().get("message"))
    elif response.status_code == 401:
        print("Unauthorized. Please log in again.")
        delete_token()
    elif response.status_code == 500:
        print("Server error occurred. Please try again later.")
    else:
        print("Response text:", response.text)
        print("Failed to perform protected action with status code:", response.status_code)


@app.command()
def whoami():
    headers = handle_authorization()
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


if __name__ == "__main__":
    app()