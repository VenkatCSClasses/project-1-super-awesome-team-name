from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, DataTable, Input, Label, Static


class FreezeAccountsModal(ModalScreen):
    """Modal to search and review accounts for freeze actions."""

    BINDINGS = [("escape", "close_modal", "Close")]

    def __init__(self) -> None:
        super().__init__()
        self.source = "suspicious"
        self.hide_frozen = False
        self.search_text = ""
        self.accounts = self.get_suspicious_accounts()
        self.filtered_accounts: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("FREEZE ACCOUNTS", classes="modal-title"),
            Static("Select a suspicious account to freeze", classes="modal-subtitle"),
            Horizontal(
                Static("Search >", classes="freeze-search-prefix"),
                Input(placeholder="type to filter by id, owner, risk, or status", id="freeze-search-input"),
                id="freeze-search-row",
            ),
            Horizontal(
                Vertical(
                    Label("Matches", classes="modal-label"),
                    DataTable(id="freeze-table"),
                    classes="freeze-left-panel",
                ),
                Vertical(
                    Label("Preview", classes="modal-label"),
                    Static("Select an account to preview details.", id="freeze-preview"),
                    classes="freeze-right-panel",
                ),
                id="freeze-main",
            ),
            Label("↑/↓ move • Enter toggles freeze state • Esc closes", id="freeze-feedback", classes="modal-feedback"),
            Horizontal(
                Button("Close", id="freeze-close", variant="default"),
                Button("Toggle Freeze", id="freeze-toggle", variant="warning"),
                id="modal-actions",
            ),
            classes="modal-container freeze-modal-container",
        )

    def on_mount(self) -> None:
        self.refresh_table()
        self.query_one("#freeze-search-input", Input).focus()

    def get_suspicious_accounts(self) -> list[dict]:
        """Return hardcoded suspicious accounts."""
        return [
            {
                "account_id": "ACC-0087",
                "owner": "mvega",
                "balance": 98210.44,
                "risk": "HIGH",
                "status": "ACTIVE",
                "reason": "9 rapid international transfers in 12 minutes",
                "last_activity": "2026-03-10 14:02:11",
            },
            {
                "account_id": "ACC-0214",
                "owner": "jlin",
                "balance": 3102.91,
                "risk": "MEDIUM",
                "status": "FROZEN",
                "reason": "Mismatched geo-IP during password reset",
                "last_activity": "2026-03-10 11:45:09",
            },
            {
                "account_id": "ACC-0771",
                "owner": "akhan",
                "balance": 40221.00,
                "risk": "HIGH",
                "status": "ACTIVE",
                "reason": "Known mule-account pattern match",
                "last_activity": "2026-03-10 08:17:55",
            },
            {
                "account_id": "ACC-0033",
                "owner": "cwong",
                "balance": 918.20,
                "risk": "MEDIUM",
                "status": "ACTIVE",
                "reason": "Repeated failed KYC verification attempts",
                "last_activity": "2026-03-09 22:51:03",
            },
        ]

    def get_all_accounts(self) -> list[dict]:
        """Return hardcoded complete account set."""
        return [
            {
                "account_id": "ACC-0001",
                "owner": "jsmith",
                "balance": 12847.53,
                "risk": "LOW",
                "status": "ACTIVE",
                "reason": "No current flags",
                "last_activity": "2026-03-10 12:11:43",
            },
            {
                "account_id": "ACC-0002",
                "owner": "jsmith",
                "balance": 45230.00,
                "risk": "LOW",
                "status": "ACTIVE",
                "reason": "No current flags",
                "last_activity": "2026-03-10 09:55:10",
            },
            {
                "account_id": "ACC-0019",
                "owner": "lgarcia",
                "balance": 223.88,
                "risk": "LOW",
                "status": "FROZEN",
                "reason": "User-requested temporary freeze",
                "last_activity": "2026-03-08 18:08:19",
            },
            {
                "account_id": "ACC-0033",
                "owner": "cwong",
                "balance": 918.20,
                "risk": "MEDIUM",
                "status": "ACTIVE",
                "reason": "Repeated failed KYC verification attempts",
                "last_activity": "2026-03-09 22:51:03",
            },
            {
                "account_id": "ACC-0087",
                "owner": "mvega",
                "balance": 98210.44,
                "risk": "HIGH",
                "status": "ACTIVE",
                "reason": "9 rapid international transfers in 12 minutes",
                "last_activity": "2026-03-10 14:02:11",
            },
            {
                "account_id": "ACC-0214",
                "owner": "jlin",
                "balance": 3102.91,
                "risk": "MEDIUM",
                "status": "FROZEN",
                "reason": "Mismatched geo-IP during password reset",
                "last_activity": "2026-03-10 11:45:09",
            },
            {
                "account_id": "ACC-0771",
                "owner": "akhan",
                "balance": 40221.00,
                "risk": "HIGH",
                "status": "ACTIVE",
                "reason": "Known mule-account pattern match",
                "last_activity": "2026-03-10 08:17:55",
            },
        ]

    def load_source_accounts(self) -> None:
        self.accounts = (
            self.get_suspicious_accounts()
            if self.source == "suspicious"
            else self.get_all_accounts()
        )

    def apply_filters(self) -> list[dict]:
        rows = self.accounts
        if self.hide_frozen:
            rows = [acc for acc in rows if acc["status"] != "FROZEN"]

        query = self.search_text.strip().lower()
        if not query:
            return rows

        filtered: list[dict] = []
        for acc in rows:
            searchable = (
                f"{acc['account_id']} {acc['owner']} {acc['risk']} "
                f"{acc['status']} {acc['reason']} {acc['last_activity']}"
            ).lower()
            if query in searchable:
                filtered.append(acc)
        return filtered

    def refresh_table(self) -> None:
        table = self.query_one("#freeze-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_column("ACCOUNT", width=14)
        table.add_column("OWNER", width=12)
        table.add_column("RISK", width=8)
        table.add_column("STATUS", width=8)

        self.load_source_accounts()
        self.filtered_accounts = self.apply_filters()
        for acc in self.filtered_accounts:
            table.add_row(
                acc["account_id"],
                acc["owner"],
                acc["risk"],
                acc["status"],
            )

        if self.filtered_accounts:
            table.move_cursor(row=0, column=0)
            self.update_preview(0)
            self.query_one("#freeze-feedback", Label).update(
                f"{len(self.filtered_accounts)} account(s) matched."
            )
        else:
            self.query_one("#freeze-preview", Static).update("No matching accounts.")
            self.query_one("#freeze-feedback", Label).update("0 accounts matched.")

    def update_preview(self, index: int) -> None:
        if index < 0 or index >= len(self.filtered_accounts):
            return

        account = self.filtered_accounts[index]
        status_color = "red" if account["status"] == "FROZEN" else "green"
        risk_color = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red"}.get(
            account["risk"], "white"
        )

        self.query_one("#freeze-preview", Static).update(
            "\n".join(
                [
                    f"[bold]Account:[/] {account['account_id']}",
                    f"[bold]Owner:[/] @{account['owner']}",
                    f"[bold]Balance:[/] ${account['balance']:,.2f}",
                    f"[bold]Risk:[/] [{risk_color}]{account['risk']}[/]",
                    f"[bold]Status:[/] [{status_color}]{account['status']}[/]",
                    f"[bold]Last Activity:[/] {account['last_activity']}",
                    "",
                    "[bold]Flag Reason[/]",
                    account["reason"],
                ]
            )
        )

    def toggle_selected_account(self) -> None:
        table = self.query_one("#freeze-table", DataTable)
        if table.cursor_row is None:
            return
        row_index = table.cursor_row
        if row_index >= len(self.filtered_accounts):
            return

        selected = self.filtered_accounts[row_index]
        new_status = "ACTIVE" if selected["status"] == "FROZEN" else "FROZEN"

        for acc in self.accounts:
            if acc["account_id"] == selected["account_id"]:
                acc["status"] = new_status

        action = "unfrozen" if new_status == "ACTIVE" else "frozen"
        self.app.notify(f"{selected['account_id']} {action} (demo)")
        self.refresh_table()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "freeze-search-input":
            self.search_text = event.value
            self.refresh_table()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "freeze-hide-frozen":
            self.hide_frozen = event.value
            self.refresh_table()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "freeze-table":
            return
        self.update_preview(event.cursor_row)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "freeze-table":
            self.toggle_selected_account()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "freeze-close":
            self.dismiss(None)
        elif event.button.id == "freeze-toggle":
            self.toggle_selected_account()
        elif event.button.id == "freeze-source-suspicious":
            self.source = "suspicious"
            self.refresh_table()
        elif event.button.id == "freeze-source-all":
            self.source = "all"
            self.refresh_table()

    def action_close_modal(self) -> None:
        self.dismiss(None)
