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
            Label("Enter an amount greater than $0.00", id="create-account-feedback", classes="modal-feedback"),
            Horizontal(
                Button("Cancel", id="create-account-cancel", variant="default"),
                Button("Create", id="create-account-submit", variant="success", disabled=True),
                id="modal-actions",
            ),
            classes="modal-container",
        )

    def get_selected_account_type(self) -> str:
        if self.query_one("#savings-radio-option", RadioButton).value:
            return "SAVINGS"
        return "CHECKING"

    def amount_validator(self, value: str) -> tuple[bool, str]:
        """Validate initial deposit amount."""
        try:
            amount = float(value)
            if amount >= 0:
                return True, ""
            return False, "Amount must be greater than or equal to zero"
        except ValueError:
            return False, "Amount must be a valid number"

    @staticmethod
    def _response_error_message(response: httpx.Response, fallback: str) -> str:
        """Extract a readable error message from an API response."""
        try:
            payload = response.json()
        except ValueError:
            return fallback
        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str) and detail:
                return detail
        return fallback

    def update_submit_state(self) -> None:
        """Enable submit only when the initial deposit is valid."""
        submit = self.query_one("#create-account-submit", Button)
        feedback = self.query_one("#create-account-feedback", Label)
        valid, message = self.amount_validator(self.query_one("#initial-deposit-input", Input).value.strip())
        if valid:
            feedback.update("[green]Amount Valid[/]")
            submit.disabled = False
        else:
            feedback.update(f"[red]{message}[/]")
            submit.disabled = True

    def on_mount(self) -> None:
        self.update_submit_state()
        self.query_one("#initial-deposit-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "initial-deposit-input":
            return
        self.update_submit_state()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-account-cancel":
            self.dismiss(None)
            return

        if event.button.id == "create-account-submit":
            raw_initial_deposit = self.query_one("#initial-deposit-input", Input).value.strip()
            valid, _ = self.amount_validator(raw_initial_deposit)
            if not valid:
                self.update_submit_state()
                return
            account_type = self.get_selected_account_type()
            initial_deposit = float(raw_initial_deposit)
            result = self.create_account(account_type, initial_deposit)
            if result is None:
                return
            self.app.notify(
                f"Account created: {account_type} with ${initial_deposit:,.2f}",
                title="[ NEW ACCOUNT ]",
            )
            self.dismiss({"account_type": account_type, "status": "created", "initial_deposit": initial_deposit})

    def action_close_modal(self) -> None:
        self.dismiss(None)

    def handle_session_expired(self) -> None:
        """Clear session token and route user back to login."""
        delete_token()
        self.app.notify("Session expired. Please log in again.", title="[ AUTH ]", severity="error")
        self.dismiss(None)
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

    def create_account(self, account_type: str, initial_balance: float) -> dict | None:
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
                    "initial_deposit": initial_balance,
                }
                response = client.post("/bank/create_bank_account", headers=headers, json=payload)
                if response.status_code in (401, 403):
                    self.handle_session_expired()
                    return None
                if response.status_code == 200:
                    return response.json()
                self.query_one("#create-account-feedback", Label).update(
                    f"[red]{self._response_error_message(response, 'Unable to create account')}[/]"
                )
                return None
            except httpx.RequestError as e:
                self.query_one("#create-account-feedback", Label).update("[red]Unable to reach the server[/]")
                print(f"Error connecting to server: {e}")
                return None
        raise Exception("Unable to create an account on the server")
