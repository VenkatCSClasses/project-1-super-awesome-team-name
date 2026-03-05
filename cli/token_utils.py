import os
from pathlib import Path
import jwt
from rich import print

# Create a path like /home/ham/.config/banking-cli/
CONFIG_DIR = Path.home() / ".config" / "banking-cli"
TOKEN_FILE = CONFIG_DIR / "token"

def save_token(token: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    TOKEN_FILE.write_text(token)
    os.chmod(TOKEN_FILE, 0o600)

def load_token() -> str:
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None

def delete_token():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def get_permissions(): 
    """Helper function to decode the token and get the user's permission level"""
    token = load_token()
    if not token:
        return -1 
    payload = jwt.decode(token, options={"verify_signature": False})
    if payload.get("permission") is not None:
        return payload.get("permission")
    return -1


def handle_authorization(skip_login_check=False):
    """Helper function to handle authorization for protected commands"""
    token = load_token()
    if not token and not skip_login_check:
        print("[red]You must be logged in to perform this action.[/red]")
        return None, -1

    payload = jwt.decode(token, options={"verify_signature": False})
    permission = payload.get("permission")
    if permission is None:
        permission = -1 # Default to not logged permission in if permission is missing
    
    headers = {"Authorization": f"Bearer {token}"}
    return headers, permission