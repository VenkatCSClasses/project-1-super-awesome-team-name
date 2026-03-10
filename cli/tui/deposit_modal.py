from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class DepositModal(ModalScreen):
    """Modal for making a demo deposit."""

    DEFAULT_CLASSES = "modal-overlay"
    BINDINGS = [("escape", "close_modal", "Close")]

    DUMMY_ACCOUNT = {
        "name": "Primary Checking",
        "id": "ACC-001",
    }

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("DEPOSIT FUNDS", classes="modal-title"),
            Static("Deposit funds into your account", classes="modal-subtitle"),
            Label("Amount", classes="modal-label"),
            Input(placeholder="$0.00", id="deposit-amount-input"),
            Static(
                f"[dim]Target:[/] {self.DUMMY_ACCOUNT['name']} ({self.DUMMY_ACCOUNT['id']})",
                classes="modal-hint",
            ),
            Label("Enter an amount greater than $0.00", id="deposit-feedback", classes="modal-feedback"),
            Horizontal(
                Button("Cancel", id="deposit-cancel", variant="default"),
                Button("Deposit", id="deposit-submit", variant="success", disabled=True),
                id="modal-actions",
            ),
            classes="modal-container",
        )

    def amount_validator(self, value: str) -> tuple[bool, str]:
        """Validate deposit amount."""
        try:
            amount = float(value)
            if amount > 0:
                return True, ""
            return False, "Amount must be greater than zero"
        except ValueError:
            return False, "Amount must be a valid number"

    def on_mount(self) -> None:
        self.query_one("#deposit-amount-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Validate and toggle submit state."""
        if event.input.id != "deposit-amount-input":
            return

        feedback = self.query_one("#deposit-feedback", Label)
        valid, message = self.amount_validator(event.value.strip())

        if valid:
            feedback.update("[green]Amount Valid[/]")
            self.query_one("#deposit-submit", Button).disabled = False
        else:
            feedback.update(f"[red]{message}[/]")
            self.query_one("#deposit-submit", Button).disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "deposit-cancel":
            self.dismiss(None)
            return

        if event.button.id == "deposit-submit":
            amount = float(self.query_one("#deposit-amount-input", Input).value.strip())
            self.app.notify(f"Demo deposit submitted: ${amount:,.2f}", title="[ DEPOSIT ]")
            self.dismiss({"amount": amount, "account_id": self.DUMMY_ACCOUNT["id"]})

    def action_close_modal(self) -> None:
        self.dismiss(None)
