from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, RadioButton, RadioSet, Static


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
            Static("[dim]Initial deposit:[/] $0.00", classes="modal-hint"),
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
            self.app.notify(
                f"Demo account created: {account_type}",
                title="[ NEW ACCOUNT ]",
            )
            self.dismiss({"account_type": account_type, "status": "created"})

    def action_close_modal(self) -> None:
        self.dismiss(None)
