import os
from typer import Typer, Option
import requests
from dotenv import load_dotenv
from token_utils import save_token, load_token, delete_token
load_dotenv()

app = Typer(no_args_is_help=True)

@app.callback()
def main():
    pass

server_base_url = os.getenv("SERVER_BASE_URL")

@app.command()
def register(username: str, password: str = Option(prompt="Create a password", hide_input=True, confirmation_prompt=True)):
    response = requests.post(f"{server_base_url}/register", json={"username": username, "password": password})
    if response.status_code == 200:
        print("Registration successful!")
        token = response.json().get("token")
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
        print("Login successful!")
        token = response.json().get("token")
        save_token(token)
    elif response.status_code == 500:
        print("Server error occurred. Please try again later.")
    else:
        print("Response text:", response.text)
        print("Login failed:", response.json().get("detail"))


@app.command()
def logout():
    delete_token()
    print("Logged out successfully!")


@app.command()
def protected_action():
    token = load_token()
    if not token:
        print("You must be logged in to perform this action.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{server_base_url}/protected", headers=headers)
    
    if response.status_code == 200:
        print("Protected action successful! Response:", response.json())
    elif response.status_code == 401:
        print("Unauthorized. Please log in again.")
        delete_token()
    elif response.status_code == 500:
        print("Server error occurred. Please try again later.")
    else:
        print("Response text:", response.text)
        print("Failed to perform protected action with status code:", response.status_code)


if __name__ == "__main__":
    app()