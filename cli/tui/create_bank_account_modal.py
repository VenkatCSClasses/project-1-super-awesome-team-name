from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, RadioButton, RadioSet, Static, Input
from token_utils import delete_token, load_token
import httpx
from dotenv import load_dotenv
import os
load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

class CreateBankAccountModal(ModalScreen):
    """Modal for creating a demo bank account."""

    DEFAULT_CLASSES = "modal-overlay"
    BINDINGS = [("escape", "close_modal", "Close")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("CREATE NEW ACCOUNT", classes="modal-title"),
            Static("Create a new bank account", classes="modal-subtitle"),
            Label("Account Type", classes="modal-label"),
            RadioSet(
                RadioButton("Checking Account", id="checking-radio-option", value=True),
                RadioButton("Savings Account", id="savings-radio-option"),
                id="account-type-options",
            ),
            Label("Initial deposit:", classes="modal-hint"),
            Input(placeholder="$0.00", id="initial-deposit-input"),
            Label("Choose the account type to create.", id="create-account-feedback", classes="modal-feedback"),
            Horizontal(
                Button("Cancel", id="create-account-cancel", variant="default"),
                Button("Create", id="create-account-submit", variant="success"),
                id="modal-actions",
            ),
            classes="modal-container",
        )

    def get_selected_account_type(self) -> str:
        if self.query_one("#savings-radio-option", RadioButton).value:
            return "SAVINGS"
        return "CHECKING"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-account-cancel":
            self.dismiss(None)
            return

        if event.button.id == "create-account-submit":
            account_type = self.get_selected_account_type()
            result = self.create_account(account_type, 0.00)
            if result is None:
                return
            self.app.notify(f"Account created: {account_type}", title="[ NEW ACCOUNT ]")
            self.dismiss({"account_type": account_type, "status": "created"})

    def action_close_modal(self) -> None:
        self.dismiss(None)

    def handle_session_expired(self) -> None:
        """Clear session token and route user back to login."""
        delete_token()
        self.app.notify("Session expired. Please log in again.", title="[ AUTH ]", severity="error")
        self.dismiss(None)
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

    def create_account(self, account_type: str, inital_balance: float) -> None:
        """Make API call to create account and handle response."""
        token = load_token()
        if not token:
            self.handle_session_expired()
            return None

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                payload = {
                    "bank_account_type": account_type,
                    "initial_deposit": 0.00,
                }
                response = client.post("/bank/create_bank_account", headers=headers, json=payload)
                if response.status_code in (401, 403):
                    self.handle_session_expired()
                    return None
                if response.status_code == 200:
                    return response.json()
                print(f"Failed to create account: {response.status_code}")
            except httpx.RequestError as e:
                print(f"Error connecting to server: {e}")
        raise Exception("Unable to create an account on the server")
