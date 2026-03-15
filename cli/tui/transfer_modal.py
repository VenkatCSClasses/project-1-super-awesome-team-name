import os

import httpx
from dotenv import load_dotenv
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from token_utils import delete_token, load_token

load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")


class TransferModal(ModalScreen):
    """Modal for transferring funds between accounts."""

    DEFAULT_CLASSES = "modal-overlay"
    BINDINGS = [("escape", "close_modal", "Close")]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source_accounts: list[dict] = []
        self.destination_account_ids: list[int] = []
        self.selected_source_account_id: int | None = None
        self.selected_destination_account_id: int | None = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("TRANSFER FUNDS", classes="modal-title"),
            Static("Move funds between bank accounts", classes="modal-subtitle"),
            Label("From Account", classes="modal-label"),
            Select([], prompt="Select a source account", id="transfer-from-select"),
            Label("To Account", classes="modal-label"),
            Select([], prompt="Select a destination account", id="transfer-to-select"),
            Label("Amount", classes="modal-label"),
            Input(placeholder="$0.00", id="transfer-amount-input"),
            Static("", id="transfer-account-hint", classes="modal-hint"),
            Label("Choose accounts and enter an amount.", id="transfer-feedback", classes="modal-feedback"),
            Horizontal(
                Button("Cancel", id="transfer-cancel", variant="default"),
                Button("Transfer", id="transfer-submit", variant="primary", disabled=True),
                id="modal-actions",
            ),
            classes="modal-container",
        )

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

    def get_user_accounts(self) -> list[dict]:
        """Fetch accounts owned by the current user for the source selector."""
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

    def get_destination_account_ids(self) -> list[int]:
        """Fetch all available account ids for transfer targets."""
        token = load_token()
        if not token:
            self.handle_session_expired()
            return []

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.get("/bank/get_all_bank_account_ids", headers=headers)
                if response.status_code == 200:
                    payload = response.json()
                    ids = payload.get("account_ids", [])
                    return [account_id for account_id in ids if isinstance(account_id, int)]
                if response.status_code in (401, 403, 404):
                    self.handle_session_expired()
                    return []
            except httpx.RequestError:
                return []
        return []

    def transfer(self, from_account_id: int, to_account_id: int, amount: float) -> dict | None:
        """Submit a transfer request."""
        token = load_token()
        if not token:
            self.handle_session_expired()
            return None

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                payload = {
                    "from_account_id": from_account_id,
                    "to_account_id": to_account_id,
                    "amount": amount,
                }
                response = client.post("/bank/transfer", headers=headers, json=payload)
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 401:
                    self.handle_session_expired()
                    return None
                self.query_one("#transfer-feedback", Label).update(
                    f"[red]{self._response_error_message(response, 'Transfer failed')}[/]"
                )
                return None
            except httpx.RequestError:
                self.query_one("#transfer-feedback", Label).update("[red]Unable to reach the server[/]")
                return None
        self.query_one("#transfer-feedback", Label).update("[red]Unable to complete transfer[/]")
        return None

    def amount_validator(self, value: str) -> tuple[bool, str]:
        """Validate transfer amount."""
        try:
            amount = float(value)
            if amount <= 0:
                return False, "Amount must be greater than zero"
            if self.selected_source_account_id is None:
                return False, "Select a source account"
            if self.selected_destination_account_id is None:
                return False, "Select a destination account"
            if self.selected_source_account_id == self.selected_destination_account_id:
                return False, "Choose a different destination account"
            account = next(
                (
                    account
                    for account in self.source_accounts
                    if account.get("account_id") == self.selected_source_account_id
                ),
                None,
            )
            if account is None:
                return False, "Select a valid source account"
            if amount > account["balance"]:
                return False, "Amount exceeds available balance"
            return True, ""
        except ValueError:
            return False, "Amount must be a valid number"

    def update_submit_state(self) -> None:
        """Enable submit only when the transfer form is valid."""
        submit = self.query_one("#transfer-submit", Button)
        feedback = self.query_one("#transfer-feedback", Label)

        if not self.source_accounts:
            submit.disabled = True
            feedback.update("[red]You have no accounts. Create one first[/]")
            return

        if not self.destination_account_ids:
            submit.disabled = True
            feedback.update("[red]No destination accounts are available[/]")
            return

        valid, message = self.amount_validator(self.query_one("#transfer-amount-input", Input).value.strip())
        if valid:
            feedback.update("[green]Transfer details look valid[/]")
            submit.disabled = False
        else:
            feedback.update(f"[red]{message}[/]")
            submit.disabled = True

    def update_account_hint(self) -> None:
        """Render current selection details."""
        hint = self.query_one("#transfer-account-hint", Static)
        source = next(
            (
                account
                for account in self.source_accounts
                if account.get("account_id") == self.selected_source_account_id
            ),
            None,
        )

        if source is None:
            if self.source_accounts:
                hint.update("[dim]Choose the account to transfer from and the destination account.[/]")
            else:
                hint.update("[dim]You have no accounts yet. Create one to get started.[/]")
            return

        destination = (
            f"ACC-{self.selected_destination_account_id}"
            if self.selected_destination_account_id is not None
            else "--"
        )
        hint.update(
            f"[dim]From:[/] ACC-{source['account_id']}  "
            f"[dim]Type:[/] {source['account_type'].upper()}  "
            f"[dim]Available:[/] ${source['balance']:,.2f}  "
            f"[dim]To:[/] {destination}"
        )

    def refresh_destination_options(self) -> None:
        """Keep the destination list in sync with the selected source account."""
        to_select = self.query_one("#transfer-to-select", Select)
        available_destinations = [
            account_id
            for account_id in self.destination_account_ids
            if account_id != self.selected_source_account_id
        ]
        to_select.set_options([(f"ACC-{account_id}", account_id) for account_id in available_destinations])

        if not available_destinations:
            self.selected_destination_account_id = None
            to_select.clear()
            return

        if self.selected_destination_account_id not in available_destinations:
            self.selected_destination_account_id = available_destinations[0]
        to_select.value = self.selected_destination_account_id

    def on_mount(self) -> None:
        self.source_accounts = self.get_user_accounts()
        self.destination_account_ids = self.get_destination_account_ids()

        from_select = self.query_one("#transfer-from-select", Select)
        from_select.set_options(
            [
                (
                    f"ACC-{account['account_id']} • {account['account_type'].upper()} • ${account['balance']:,.2f}",
                    account["account_id"],
                )
                for account in self.source_accounts
            ]
        )

        to_select = self.query_one("#transfer-to-select", Select)

        if self.source_accounts:
            self.selected_source_account_id = self.source_accounts[0]["account_id"]
            from_select.value = self.selected_source_account_id
        self.refresh_destination_options()

        self.update_account_hint()
        self.update_submit_state()
        self.query_one("#transfer-amount-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "transfer-amount-input":
            return
        self.update_submit_state()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "transfer-from-select":
            self.selected_source_account_id = event.value if event.value != Select.BLANK else None
            self.refresh_destination_options()
        elif event.select.id == "transfer-to-select":
            self.selected_destination_account_id = event.value if event.value != Select.BLANK else None
        else:
            return

        self.update_account_hint()
        self.update_submit_state()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "transfer-cancel":
            self.dismiss(None)
            return

        if event.button.id == "transfer-submit":
            amount = float(self.query_one("#transfer-amount-input", Input).value.strip())
            if self.selected_source_account_id is None or self.selected_destination_account_id is None:
                self.update_submit_state()
                return
            result = self.transfer(
                self.selected_source_account_id,
                self.selected_destination_account_id,
                amount,
            )
            if result is None:
                return
            self.app.notify(
                f"Transferred ${amount:,.2f} to ACC-{self.selected_destination_account_id}",
                title="[ TRANSFER ]",
            )
            self.dismiss(
                {
                    "amount": amount,
                    "from_account_id": self.selected_source_account_id,
                    "to_account_id": self.selected_destination_account_id,
                    "result": result,
                }
            )

    def action_close_modal(self) -> None:
        self.dismiss(None)
