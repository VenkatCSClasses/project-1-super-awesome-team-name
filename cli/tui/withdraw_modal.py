from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class WithdrawModal(ModalScreen):
    """Modal for making a demo withdrawal."""

    DEFAULT_CLASSES = "modal-overlay"
    BINDINGS = [("escape", "close_modal", "Close")]

    DUMMY_ACCOUNT = {
        "name": "Primary Checking",
        "id": "ACC-001",
        "balance": 12847.53,
    }

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("WITHDRAW FUNDS", classes="modal-title"),
            Static("Withdraw funds from your account", classes="modal-subtitle"),
            Label("Amount", classes="modal-label"),
            Input(placeholder="$0.00", id="withdraw-amount-input"),
            Static(
                f"[dim]From:[/] {self.DUMMY_ACCOUNT['name']} ({self.DUMMY_ACCOUNT['id']})  "
                f"[dim]Available:[/] ${self.DUMMY_ACCOUNT['balance']:,.2f}",
                classes="modal-hint",
            ),
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
            if amount > self.DUMMY_ACCOUNT["balance"]:
                return False, "Amount exceeds available balance"
            return True, ""
        except ValueError:
            return False, "Amount must be a valid number"

    def on_mount(self) -> None:
        self.query_one("#withdraw-amount-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "withdraw-amount-input":
            return

        feedback = self.query_one("#withdraw-feedback", Label)
        valid, message = self.amount_validator(event.value.strip())

        if valid:
            feedback.update("[green]Amount Valid[/]")
            self.query_one("#withdraw-submit", Button).disabled = False
        else:
            feedback.update(f"[red]{message}[/]")
            self.query_one("#withdraw-submit", Button).disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "withdraw-cancel":
            self.dismiss(None)
            return

        if event.button.id == "withdraw-submit":
            amount = float(self.query_one("#withdraw-amount-input", Input).value.strip())
            self.app.notify(f"Demo withdrawal submitted: ${amount:,.2f}", title="[ WITHDRAW ]")
            self.dismiss({"amount": amount, "account_id": self.DUMMY_ACCOUNT["id"]})

    def action_close_modal(self) -> None:
        self.dismiss(None)
