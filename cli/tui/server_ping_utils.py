from dotenv import load_dotenv
import os
import requests
load_dotenv()


def server_running() -> bool: 
    """Simple function to test server connectivity."""
    load_dotenv()
    SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

    try:
        response = requests.get(f"{SERVER_BASE_URL}", timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"Server responded with status code {response.status_code}.")
    except requests.RequestException as e:
        return False