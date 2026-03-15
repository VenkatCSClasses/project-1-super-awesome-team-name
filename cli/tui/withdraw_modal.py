import os

import httpx
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static
from dotenv import load_dotenv

from token_utils import delete_token, load_token

load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")


class WithdrawModal(ModalScreen):
    """Modal for making a demo withdrawal."""

    DEFAULT_CLASSES = "modal-overlay"
    BINDINGS = [("escape", "close_modal", "Close")]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.accounts: list[dict] = []
        self.selected_account_id: int | None = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("WITHDRAW FUNDS", classes="modal-title"),
            Static("Withdraw funds from your account", classes="modal-subtitle"),
            Label("Source Account", classes="modal-label"),
            Select([], prompt="Select an account", id="withdraw-account-select"),
            Label("Amount", classes="modal-label"),
            Input(placeholder="$0.00", id="withdraw-amount-input"),
            Static("", id="withdraw-account-hint", classes="modal-hint"),
            Label(
                "Enter an amount up to the available balance.",
                id="withdraw-feedback",
                classes="modal-feedback",
            ),
            Horizontal(
                Button("Cancel", id="withdraw-cancel", variant="default"),
                Button("Withdraw", id="withdraw-submit", variant="warning", disabled=True),
                id="modal-actions",
            ),
            classes="modal-container",
        )

    def amount_validator(self, value: str) -> tuple[bool, str]:
        """Validate withdrawal amount."""
        try:
            amount = float(value)
            if amount <= 0:
                return False, "Amount must be greater than zero"
            account = next(
                (account for account in self.accounts if account.get("account_id") == self.selected_account_id),
                None,
            )
            if account is None:
                return False, "Select an account to withdraw from"
            if amount > account["balance"]:
                return False, "Amount exceeds available balance"
            return True, ""
        except ValueError:
            return False, "Amount must be a valid number"

    def handle_session_expired(self) -> None:
        """Clear session token and route user back to login."""
        delete_token()
        self.app.notify("Session expired. Please log in again.", title="[ AUTH ]", severity="error")
        self.dismiss(None)
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

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

    def get_accounts(self) -> list[dict]:
        """Fetch available accounts for the current user."""
        token = load_token()
        if not token:
            self.handle_session_expired()
            return []

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.get("/bank/get_all_bank_accounts", headers=headers)
                if response.status_code == 200:
                    payload = response.json()
                    accounts = payload.get("accounts", [])
                    return [account for account in accounts if isinstance(account, dict)]
                if response.status_code in (401, 403, 404):
                    self.handle_session_expired()
                    return []
            except httpx.RequestError:
                return []
        return []

    def update_submit_state(self) -> None:
        """Enable submit only when the form is valid."""
        submit = self.query_one("#withdraw-submit", Button)
        feedback = self.query_one("#withdraw-feedback", Label)

        if self.selected_account_id is None:
            submit.disabled = True
            if self.accounts:
                feedback.update("[red]Select an account to withdraw from[/]")
            else:
                feedback.update("[red]You have no accounts. Create one first[/]")
            return

        valid, message = self.amount_validator(self.query_one("#withdraw-amount-input", Input).value.strip())
        if valid:
            feedback.update("[green]Amount Valid[/]")
            submit.disabled = False
        else:
            feedback.update(f"[red]{message}[/]")
            submit.disabled = True

    def update_account_hint(self) -> None:
        """Show the current account selection details."""
        hint = self.query_one("#withdraw-account-hint", Static)
        account = next(
            (account for account in self.accounts if account.get("account_id") == self.selected_account_id),
            None,
        )
        if account is None:
            if self.accounts:
                hint.update("[dim]Choose which account to withdraw from.[/]")
            else:
                hint.update("[dim]You have no accounts yet. Create one to get started.[/]")
            return

        hint.update(
            f"[dim]From:[/] ACC-{account['account_id']}  "
            f"[dim]Type:[/] {account['account_type'].upper()}  "
            f"[dim]Available:[/] ${account['balance']:,.2f}"
        )

    def withdraw(self, account_id: int, amount: float) -> dict | None:
        """Submit a withdrawal request."""
        token = load_token()
        if not token:
            self.handle_session_expired()
            return None

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.post(
                    "/bank/withdraw",
                    headers=headers,
                    json={"account_id": account_id, "amount": amount},
                )
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 401:
                    self.handle_session_expired()
                    return None
                self.query_one("#withdraw-feedback", Label).update(
                    f"[red]{self._response_error_message(response, 'Unable to complete withdrawal')}[/]"
                )
                return None
            except httpx.RequestError:
                self.query_one("#withdraw-feedback", Label).update("[red]Unable to reach the server[/]")
                return None

    def on_mount(self) -> None:
        self.accounts = self.get_accounts()
        account_select = self.query_one("#withdraw-account-select", Select)
        options = [
            (
                f"ACC-{account['account_id']} • {account['account_type'].upper()} • ${account['balance']:,.2f}",
                account["account_id"],
            )
            for account in self.accounts
        ]
        account_select.set_options(options)
        if self.accounts:
            self.selected_account_id = self.accounts[0]["account_id"]
            account_select.value = self.selected_account_id
        self.update_account_hint()
        self.update_submit_state()
        self.query_one("#withdraw-amount-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "withdraw-amount-input":
            return

        self.update_submit_state()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "withdraw-account-select":
            return

        self.selected_account_id = event.value if event.value != Select.BLANK else None
        self.update_account_hint()
        self.update_submit_state()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "withdraw-cancel":
            self.dismiss(None)
            return

        if event.button.id == "withdraw-submit":
            amount = float(self.query_one("#withdraw-amount-input", Input).value.strip())
            if self.selected_account_id is None:
                self.update_submit_state()
                return
            result = self.withdraw(self.selected_account_id, amount)
            if result is None:
                return
            self.app.notify(f"Withdrew ${amount:,.2f} from ACC-{self.selected_account_id}", title="[ WITHDRAW ]")
            self.dismiss(
                {
                    "amount": amount,
                    "account_id": self.selected_account_id,
                    "result": result,
                }
            )

    def action_close_modal(self) -> None:
        self.dismiss(None)
