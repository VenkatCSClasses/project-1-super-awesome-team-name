import os
from pathlib import Path

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