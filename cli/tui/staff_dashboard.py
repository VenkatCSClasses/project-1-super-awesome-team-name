from __future__ import annotations

import jwt
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, ContentSwitcher, DataTable, Footer, Header, Input, Label, Select, Static

from token_utils import delete_token, load_token


@dataclass
class MockBankStore:
    users: list[dict]
    accounts: list[dict]
    next_user_id: int
    next_account_id: int


_MOCK_BANK_STORE = MockBankStore(
    users=[
        {"user_id": 1001, "username": "maria", "permission": 0, "status": "ACTIVE", "account_count": 2},
        {"user_id": 1002, "username": "owen", "permission": 0, "status": "ACTIVE", "account_count": 1},
        {"user_id": 1003, "username": "teller.jules", "permission": 1, "status": "ACTIVE", "account_count": 0},
        {"user_id": 1004, "username": "admin.lee", "permission": 2, "status": "ACTIVE", "account_count": 0},
        {"user_id": 1005, "username": "rina", "permission": 0, "status": "ACTIVE", "account_count": 1},
        {"user_id": 1006, "username": "noah", "permission": 0, "status": "ACTIVE", "account_count": 0},
    ],
    accounts=[
        {
            "account_id": 41001,
            "user_id": 1001,
            "owner": "maria",
            "account_type": "CHECKING",
            "balance": 4821.11,
            "status": "ACTIVE",
            "is_frozen": False,
            "is_suspicious": False,
            "suspicious_reason": "",
            "last_activity": "2026-03-14 08:11:02",
        },
        {
            "account_id": 41002,
            "user_id": 1001,
            "owner": "maria",
            "account_type": "SAVINGS",
            "balance": 21340.55,
            "status": "ACTIVE",
            "is_frozen": False,
            "is_suspicious": True,
            "suspicious_reason": "6 large transfers posted inside 9 minutes",
            "last_activity": "2026-03-14 09:42:18",
        },
        {
            "account_id": 41003,
            "user_id": 1002,
            "owner": "owen",
            "account_type": "CHECKING",
            "balance": 91.48,
            "status": "ACTIVE",
            "is_frozen": False,
            "is_suspicious": False,
            "suspicious_reason": "",
            "last_activity": "2026-03-13 17:02:41",
        },
        {
            "account_id": 41004,
            "user_id": 1005,
            "owner": "rina",
            "account_type": "SAVINGS",
            "balance": 76002.10,
            "status": "FROZEN",
            "is_frozen": True,
            "is_suspicious": True,
            "suspicious_reason": "Known mule-account pattern plus geo mismatch",
            "last_activity": "2026-03-14 07:54:07",
        },
    ],
    next_user_id=1007,
    next_account_id=41005,
)


def _permission_label(permission: int) -> str:
    return {0: "CUSTOMER", 1: "TELLER", 2: "ADMIN"}.get(permission, "UNKNOWN")


def _permission_color(permission: int) -> str:
    return {0: "yellow", 1: "cyan", 2: "red"}.get(permission, "white")


def _decode_current_token() -> dict:
    token = load_token()
    if not token:
        return {"username": "unknown", "user_id": "unknown", "permission": -1}
    payload = jwt.decode(token, options={"verify_signature": False})
    return {
        "username": payload.get("sub", payload.get("username", "unknown")),
        "user_id": str(payload.get("user_id", "unknown")),
        "permission": payload.get("permission", -1),
    }


def mock_get_staff_user_info() -> dict:
    return _decode_current_token()


def mock_get_all_users() -> list[dict]:
    return [user.copy() for user in _MOCK_BANK_STORE.users]


def mock_get_managed_accounts() -> list[dict]:
    return [account.copy() for account in _MOCK_BANK_STORE.accounts]


def mock_get_bank_total_balance() -> float:
    return sum(account["balance"] for account in _MOCK_BANK_STORE.accounts)


def mock_get_accounts_for_user(user_id: int) -> list[dict]:
    return [account.copy() for account in _MOCK_BANK_STORE.accounts if account["user_id"] == user_id]


def mock_get_suspicious_accounts() -> list[dict]:
    return [account.copy() for account in _MOCK_BANK_STORE.accounts if account["is_suspicious"]]


def mock_create_user(username: str, permission: int) -> dict:
    if any(user["username"] == username for user in _MOCK_BANK_STORE.users):
        raise ValueError(f"User @{username} already exists")
    user = {
        "user_id": _MOCK_BANK_STORE.next_user_id,
        "username": username,
        "permission": permission,
        "status": "ACTIVE",
        "account_count": 0,
    }
    _MOCK_BANK_STORE.next_user_id += 1
    _MOCK_BANK_STORE.users.append(user)
    return user.copy()


def mock_delete_user(user_id: int) -> dict:
    for index, user in enumerate(_MOCK_BANK_STORE.users):
        if user["user_id"] != user_id:
            continue
        if any(account["user_id"] == user_id for account in _MOCK_BANK_STORE.accounts):
            raise ValueError("Delete or close this user's accounts first")
        return _MOCK_BANK_STORE.users.pop(index).copy()
    raise ValueError(f"User USER-{user_id} does not exist")


def mock_create_account(username: str, account_type: str, opening_balance: float) -> dict:
    owner = next((user for user in _MOCK_BANK_STORE.users if user["username"] == username), None)
    if owner is None:
        raise ValueError(f"User @{username} does not exist")
    account = {
        "account_id": _MOCK_BANK_STORE.next_account_id,
        "user_id": owner["user_id"],
        "owner": owner["username"],
        "account_type": account_type.upper(),
        "balance": opening_balance,
        "status": "ACTIVE",
        "is_frozen": False,
        "is_suspicious": opening_balance >= 50000,
        "suspicious_reason": "High opening balance threshold exceeded" if opening_balance >= 50000 else "",
        "last_activity": "2026-03-14 10:15:00",
    }
    _MOCK_BANK_STORE.next_account_id += 1
    _MOCK_BANK_STORE.accounts.append(account)
    owner["account_count"] += 1
    return account.copy()


def mock_close_account(account_id: int) -> dict:
    for index, account in enumerate(_MOCK_BANK_STORE.accounts):
        if account["account_id"] != account_id:
            continue
        removed = _MOCK_BANK_STORE.accounts.pop(index)
        owner = next((user for user in _MOCK_BANK_STORE.users if user["user_id"] == removed["user_id"]), None)
        if owner and owner["account_count"] > 0:
            owner["account_count"] -= 1
        return removed.copy()
    raise ValueError(f"Account ACC-{account_id} does not exist")


def mock_toggle_account_freeze(account_id: int) -> dict:
    for account in _MOCK_BANK_STORE.accounts:
        if account["account_id"] == account_id:
            account["is_frozen"] = not account["is_frozen"]
            account["status"] = "FROZEN" if account["is_frozen"] else "ACTIVE"
            return account.copy()
    raise ValueError(f"Account ACC-{account_id} does not exist")


class StaffActionModal(ModalScreen):
    BINDINGS = [Binding("escape", "close_modal", "Close")]

    def __init__(self, title: str, subtitle: str, fields: list[dict]) -> None:
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.fields = fields

    def compose(self) -> ComposeResult:
        children: list = [
            Static(self.title, classes="modal-title"),
            Static(self.subtitle, classes="modal-subtitle"),
        ]
        for field in self.fields:
            children.append(Label(field["label"], classes="modal-label"))
            if field["kind"] == "select":
                children.append(
                    Select(
                        field["options"],
                        id=field["id"],
                        value=field.get("value"),
                        allow_blank=False,
                    )
                )
            else:
                children.append(
                    Input(
                        placeholder=field.get("placeholder", ""),
                        id=field["id"],
                        value=field.get("value", ""),
                    )
                )
        children.extend(
            [
                Label("", classes="modal-feedback"),
                Horizontal(
                    Button("Cancel", id="staff-modal-cancel"),
                    Button("Submit", id="staff-modal-submit", variant="success"),
                    id="modal-actions",
                ),
            ]
        )
        yield Vertical(*children, classes="modal-container")

    def on_mount(self) -> None:
        first_input = self.query("Input, Select").first()
        if first_input is not None:
            first_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "staff-modal-cancel":
            self.dismiss(None)
            return
        if event.button.id != "staff-modal-submit":
            return

        values: dict[str, object] = {}
        for field in self.fields:
            if field["kind"] == "select":
                values[field["id"]] = self.query_one(f"#{field['id']}", Select).value
            else:
                values[field["id"]] = self.query_one(f"#{field['id']}", Input).value.strip()
        self.dismiss(values)

    def action_close_modal(self) -> None:
        self.dismiss(None)


class UserDirectoryBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("USER DIRECTORY", classes="box-top")
        yield Horizontal(
            Static("Search >", classes="staff-search-prefix"),
            Input(placeholder="username, id, role, or status", id="staff-user-search"),
            id="staff-user-search-row",
        )
        yield Static("", id="staff-user-status")
        yield DataTable(id="staff-user-table")


class SelectedUserBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("SELECTED USER", classes="box-top")
        yield Static("", id="staff-user-preview")


class SelectedUserAccountsBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("SELECTED USER ACCOUNTS", classes="box-top")
        yield Static("", id="staff-user-accounts-status")
        yield DataTable(id="staff-user-accounts-table")


class SuspiciousAccountsBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("SUSPICIOUS ACTIVITY", classes="box-top")
        yield Static("", id="staff-suspicious-status")
        yield DataTable(id="staff-suspicious-table")


class SuspiciousPreviewBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("FLAG DETAILS", classes="box-top")
        yield Static("", id="staff-suspicious-preview")


class StaffDashboardScreen(Screen):
    SUB_TITLE = "Staff Dashboard"

    BINDINGS = [
        Binding("q", "logout", "Logout"),
        Binding("r", "refresh", "Refresh"),
        Binding("u", "show_users_page", "Users"),
        Binding("s", "show_suspicious_page", "Suspicious"),
        Binding("n", "create_user", "Create User"),
        Binding("a", "create_account", "Create Account"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.user = mock_get_staff_user_info()
        self.permission = self.user.get("permission", -1)
        self.current_page = "users-page"
        self.user_search = ""
        self.users_data: list[dict] = []
        self.filtered_users: list[dict] = []
        self.accounts_data: list[dict] = []
        self.selected_user_id: int | None = None
        self.selected_user_account_id: int | None = None
        self.selected_suspicious_account_id: int | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            self._build_user_info_box(),
            self._build_summary_box(),
            id="staff-top-row",
        )
        yield Horizontal(
            Button("USER MANAGEMENT", id="staff-users-page-btn", variant="primary"),
            Button("SUSPICIOUS ACTIVITY", id="staff-suspicious-page-btn", variant="warning", disabled=self.permission < 2),
            id="staff-page-nav",
        )
        yield ContentSwitcher(
            Vertical(
                Horizontal(
                    UserDirectoryBox(id="staff-user-directory-box"),
                    Vertical(
                        SelectedUserBox(id="staff-selected-user-box"),
                        SelectedUserAccountsBox(id="staff-user-accounts-box"),
                        id="staff-user-right-rail",
                    ),
                    id="staff-users-layout",
                ),
                Horizontal(
                    Button("CREATE USER", id="staff-create-user-btn", variant="success", disabled=self.permission < 2),
                    Button("DELETE USER", id="staff-delete-user-btn", variant="error", disabled=self.permission < 2),
                    Button("CREATE ACCOUNT", id="staff-create-account-btn", variant="success"),
                    Button("CLOSE ACCOUNT", id="staff-close-account-btn", variant="warning"),
                    Button("REFRESH", id="staff-users-refresh-btn", variant="primary"),
                    id="staff-users-actions",
                ),
                id="users-page",
            ),
            Vertical(
                Horizontal(
                    SuspiciousAccountsBox(id="staff-suspicious-box"),
                    SuspiciousPreviewBox(id="staff-suspicious-preview-box"),
                    id="staff-suspicious-layout",
                ),
                Horizontal(
                    Button("FREEZE / UNFREEZE", id="staff-freeze-account-btn", variant="warning", disabled=self.permission < 2),
                    Button("REFRESH", id="staff-suspicious-refresh-btn", variant="primary"),
                    id="staff-suspicious-actions",
                ),
                id="suspicious-page",
            ),
            initial="users-page",
            id="staff-page-switcher",
        )
        yield Horizontal(
            Button("LOGOUT", id="staff-logout-btn", variant="error"),
            id="action-bar",
        )
        yield Footer()

    def _build_user_info_box(self) -> Container:
        color = _permission_color(self.permission)
        access = _permission_label(self.permission)
        return Container(
            Static("USER SESSION", classes="box-top"),
            Static(
                f"  [dim]Username:[/] [bold {color}]@{self.user['username']}[/]\n"
                f"  [dim]ID:[/] USER-{self.user['user_id']}\n"
                f"  [dim]Access Level:[/] [{color}]{access}[/]",
                id="user-details",
            ),
            id="user-info-box",
        )

    def _build_summary_box(self) -> Container:
        return Container(
            Static("OPERATIONS SUMMARY", classes="box-top"),
            Static("", id="staff-summary-content"),
            id="staff-summary-box",
        )

    def on_mount(self) -> None:
        self._refresh_dashboard_view()

    def _load_data(self) -> None:
        self.users_data = mock_get_all_users()
        self.accounts_data = mock_get_managed_accounts()

    def _apply_user_filter(self) -> list[dict]:
        query = self.user_search.strip().lower()
        if not query:
            return list(self.users_data)
        filtered: list[dict] = []
        for user in self.users_data:
            searchable = (
                f"{user['username']} {user['user_id']} "
                f"{_permission_label(user['permission'])} {user['status']} {user['account_count']}"
            ).lower()
            if query in searchable:
                filtered.append(user)
        return filtered

    def _refresh_dashboard_view(self, notify: bool = False) -> None:
        self._load_data()
        self.filtered_users = self._apply_user_filter()
        user_ids = {user["user_id"] for user in self.filtered_users}
        all_account_ids = {account["account_id"] for account in self.accounts_data}
        suspicious_ids = {account["account_id"] for account in mock_get_suspicious_accounts()}

        if self.selected_user_id not in user_ids:
            self.selected_user_id = self.filtered_users[0]["user_id"] if self.filtered_users else None

        user_accounts = mock_get_accounts_for_user(self.selected_user_id) if self.selected_user_id is not None else []
        user_account_ids = {account["account_id"] for account in user_accounts}
        if self.selected_user_account_id not in user_account_ids:
            self.selected_user_account_id = user_accounts[0]["account_id"] if user_accounts else None

        if self.selected_suspicious_account_id not in suspicious_ids:
            suspicious_accounts = mock_get_suspicious_accounts()
            self.selected_suspicious_account_id = suspicious_accounts[0]["account_id"] if suspicious_accounts else None

        self._render_summary()
        self._render_user_table()
        self._render_selected_user()
        self._render_selected_user_accounts()
        self._render_suspicious_table()
        self._render_suspicious_preview()
        self._sync_page_buttons()
        if notify:
            self.notify("Management view refreshed.", title="[ REFRESH ]", severity="information")

    def _render_summary(self) -> None:
        suspicious_count = len(mock_get_suspicious_accounts())
        frozen_count = sum(1 for account in self.accounts_data if account["is_frozen"])
        summary_lines = [
            f"  [dim]Users:[/] [bold]{len(self.users_data)}[/]",
            f"  [dim]Accounts:[/] [bold]{len(self.accounts_data)}[/]",
            f"  [dim]Suspicious:[/] [yellow]{suspicious_count}[/]",
            f"  [dim]Frozen:[/] [red]{frozen_count}[/]",
        ]
        if self.permission >= 2:
            summary_lines.insert(
                0,
                f"  [dim]Bank Total:[/] [bold green]${mock_get_bank_total_balance():,.2f}[/]",
            )
        else:
            summary_lines.append("  [dim]Scope:[/] [cyan]Teller management view[/]")
        self.query_one("#staff-summary-content", Static).update("\n".join(summary_lines))

    def _render_user_table(self) -> None:
        table = self.query_one("#staff-user-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_column("USER", width=18)
        table.add_column("ID", width=10)
        table.add_column("ROLE", width=10)
        table.add_column("STATUS", width=10)
        table.add_column("ACCTS", width=8)

        for index, user in enumerate(self.filtered_users):
            table.add_row(
                f"@{user['username']}",
                f"USER-{user['user_id']}",
                _permission_label(user["permission"]),
                user["status"],
                str(user["account_count"]),
            )
            if user["user_id"] == self.selected_user_id:
                table.move_cursor(row=index, column=0)

        status_text = (
            f"  [dim]{len(self.filtered_users)} user(s) matched the current search.[/]"
            if self.filtered_users
            else "  [dim]No users matched the current search.[/]"
        )
        self.query_one("#staff-user-status", Static).update(status_text)

    def _render_selected_user(self) -> None:
        selected = next((user for user in self.users_data if user["user_id"] == self.selected_user_id), None)
        if selected is None:
            self.query_one("#staff-user-preview", Static).update("No user selected.")
            return

        related_accounts = mock_get_accounts_for_user(selected["user_id"])
        flagged_accounts = sum(1 for account in related_accounts if account["is_suspicious"])
        self.query_one("#staff-user-preview", Static).update(
            "\n".join(
                [
                    f"[bold]User:[/] @{selected['username']}",
                    f"[bold]ID:[/] USER-{selected['user_id']}",
                    f"[bold]Role:[/] {_permission_label(selected['permission'])}",
                    f"[bold]Status:[/] {selected['status']}",
                    f"[bold]Accounts:[/] {len(related_accounts)}",
                    f"[bold]Flagged:[/] [yellow]{flagged_accounts}[/]",
                    "",
                    "[dim]Create accounts, close the selected account, or delete the user if they have no accounts.[/]",
                ]
            )
        )

    def _render_selected_user_accounts(self) -> None:
        table = self.query_one("#staff-user-accounts-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_column("ACCOUNT", width=12)
        table.add_column("TYPE", width=10)
        table.add_column("BALANCE", width=14)
        table.add_column("STATUS", width=10)
        table.add_column("FLAG", width=12)

        if self.selected_user_id is None:
            self.query_one("#staff-user-accounts-status", Static).update("  [dim]Select a user to view accounts.[/]")
            return

        user_accounts = mock_get_accounts_for_user(self.selected_user_id)
        for index, account in enumerate(user_accounts):
            table.add_row(
                f"ACC-{account['account_id']}",
                account["account_type"],
                f"${account['balance']:,.2f}",
                account["status"],
                "SUSPICIOUS" if account["is_suspicious"] else "CLEAR",
            )
            if account["account_id"] == self.selected_user_account_id:
                table.move_cursor(row=index, column=0)

        if user_accounts:
            self.query_one("#staff-user-accounts-status", Static).update(
                f"  [dim]Showing {len(user_accounts)} account(s) for the selected user.[/]"
            )
        else:
            self.query_one("#staff-user-accounts-status", Static).update(
                "  [dim]The selected user does not have any accounts.[/]"
            )

    def _render_suspicious_table(self) -> None:
        table = self.query_one("#staff-suspicious-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_column("ACCOUNT", width=12)
        table.add_column("OWNER", width=16)
        table.add_column("BALANCE", width=14)
        table.add_column("STATUS", width=10)
        table.add_column("LAST ACTIVITY", width=20)

        suspicious_accounts = mock_get_suspicious_accounts()
        for index, account in enumerate(suspicious_accounts):
            table.add_row(
                f"ACC-{account['account_id']}",
                f"@{account['owner']}",
                f"${account['balance']:,.2f}",
                account["status"],
                account["last_activity"],
            )
            if account["account_id"] == self.selected_suspicious_account_id:
                table.move_cursor(row=index, column=0)

        status_text = (
            f"  [dim]{len(suspicious_accounts)} suspicious account(s) in the queue.[/]"
            if suspicious_accounts
            else "  [dim]No suspicious accounts in mock data.[/]"
        )
        self.query_one("#staff-suspicious-status", Static).update(status_text)

    def _render_suspicious_preview(self) -> None:
        if self.permission < 2:
            self.query_one("#staff-suspicious-preview", Static).update(
                "Admins can review suspicious activity and freeze or unfreeze accounts."
            )
            return

        suspicious_accounts = mock_get_suspicious_accounts()
        selected = next(
            (account for account in suspicious_accounts if account["account_id"] == self.selected_suspicious_account_id),
            None,
        )
        if selected is None:
            self.query_one("#staff-suspicious-preview", Static).update("No suspicious account selected.")
            return

        status_color = "red" if selected["is_frozen"] else "green"
        self.query_one("#staff-suspicious-preview", Static).update(
            "\n".join(
                [
                    f"[bold]Account:[/] ACC-{selected['account_id']}",
                    f"[bold]Owner:[/] @{selected['owner']}",
                    f"[bold]Balance:[/] ${selected['balance']:,.2f}",
                    f"[bold]Status:[/] [{status_color}]{selected['status']}[/]",
                    f"[bold]Last Activity:[/] {selected['last_activity']}",
                    "",
                    "[bold]Reason[/]",
                    selected["suspicious_reason"] or "No reason supplied.",
                ]
            )
        )

    def _sync_page_buttons(self) -> None:
        users_button = self.query_one("#staff-users-page-btn", Button)
        suspicious_button = self.query_one("#staff-suspicious-page-btn", Button)
        users_button.variant = "primary" if self.current_page == "users-page" else "default"
        suspicious_button.variant = "warning" if self.current_page == "suspicious-page" else "default"
        self.query_one("#staff-page-switcher", ContentSwitcher).current = self.current_page

    def _selected_user(self) -> dict | None:
        return next((user for user in self.users_data if user["user_id"] == self.selected_user_id), None)

    def _selected_user_account(self) -> dict | None:
        if self.selected_user_id is None:
            return None
        return next(
            (
                account
                for account in mock_get_accounts_for_user(self.selected_user_id)
                if account["account_id"] == self.selected_user_account_id
            ),
            None,
        )

    def _selected_suspicious_account(self) -> dict | None:
        return next(
            (
                account
                for account in mock_get_suspicious_accounts()
                if account["account_id"] == self.selected_suspicious_account_id
            ),
            None,
        )

    def _open_create_user_modal(self) -> None:
        if self.permission < 2:
            self.notify("Only admins can create users.", title="[ USER ]", severity="warning")
            return
        self.app.push_screen(
            StaffActionModal(
                "CREATE USER",
                "Mock form only. Replace this handler with your API call later.",
                [
                    {"id": "new-username", "label": "Username", "kind": "input", "placeholder": "new.user"},
                    {
                        "id": "new-permission",
                        "label": "Permission",
                        "kind": "select",
                        "options": [("CUSTOMER", 0), ("TELLER", 1), ("ADMIN", 2)],
                        "value": 0,
                    },
                ],
            ),
            self._handle_create_user,
        )

    def _open_create_account_modal(self) -> None:
        selected_user = self._selected_user()
        user_options = [
            (f"@{user['username']} ({_permission_label(user['permission'])})", user["username"])
            for user in self.users_data
        ]
        self.app.push_screen(
            StaffActionModal(
                "CREATE ACCOUNT",
                "Creates a mock account for the selected user.",
                [
                    {
                        "id": "account-owner",
                        "label": "Owner",
                        "kind": "select",
                        "options": user_options,
                        "value": selected_user["username"] if selected_user else (user_options[0][1] if user_options else None),
                    },
                    {
                        "id": "account-type",
                        "label": "Account Type",
                        "kind": "select",
                        "options": [("CHECKING", "CHECKING"), ("SAVINGS", "SAVINGS")],
                        "value": "CHECKING",
                    },
                    {"id": "opening-balance", "label": "Opening Balance", "kind": "input", "placeholder": "0.00", "value": "0.00"},
                ],
            ),
            self._handle_create_account,
        )

    def _handle_create_user(self, result: dict | None) -> None:
        if result is None:
            return
        try:
            created = mock_create_user(str(result["new-username"]), int(result["new-permission"]))
        except ValueError as error:
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_id = created["user_id"]
        self.current_page = "users-page"
        self._refresh_dashboard_view()
        self.notify(f"Created @{created['username']} with {_permission_label(created['permission'])} access (mock).", title="[ USER ]")

    def _handle_create_account(self, result: dict | None) -> None:
        if result is None:
            return
        try:
            created = mock_create_account(
                str(result["account-owner"]),
                str(result["account-type"]),
                float(str(result["opening-balance"]) or "0"),
            )
        except ValueError as error:
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_id = created["user_id"]
        self.selected_user_account_id = created["account_id"]
        self.selected_suspicious_account_id = created["account_id"] if created["is_suspicious"] else self.selected_suspicious_account_id
        self.current_page = "users-page"
        self._refresh_dashboard_view()
        self.notify(f"Created ACC-{created['account_id']} for @{created['owner']} (mock).", title="[ ACCOUNT ]")

    def _delete_selected_user(self) -> None:
        if self.permission < 2:
            self.notify("Only admins can delete users.", title="[ USER ]", severity="warning")
            return
        selected = self._selected_user()
        if selected is None:
            self.notify("Select a user first.", title="[ USER ]", severity="warning")
            return
        try:
            deleted = mock_delete_user(selected["user_id"])
        except ValueError as error:
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_id = None
        self.selected_user_account_id = None
        self._refresh_dashboard_view()
        self.notify(f"Deleted @{deleted['username']} (mock).", title="[ USER ]")

    def _close_selected_account(self) -> None:
        selected = self._selected_user_account()
        if selected is None:
            self.notify("Select an account first.", title="[ ACCOUNT ]", severity="warning")
            return
        try:
            closed = mock_close_account(selected["account_id"])
        except ValueError as error:
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_account_id = None
        if self.selected_suspicious_account_id == closed["account_id"]:
            self.selected_suspicious_account_id = None
        self._refresh_dashboard_view()
        self.notify(f"Closed ACC-{closed['account_id']} (mock).", title="[ ACCOUNT ]")

    def _toggle_selected_account_freeze(self) -> None:
        if self.permission < 2:
            self.notify("Only admins can freeze accounts.", title="[ ACCOUNT ]", severity="warning")
            return
        selected = self._selected_suspicious_account()
        if selected is None:
            self.notify("Select a suspicious account first.", title="[ ACCOUNT ]", severity="warning")
            return
        try:
            updated = mock_toggle_account_freeze(selected["account_id"])
        except ValueError as error:
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_suspicious_account_id = updated["account_id"]
        self._refresh_dashboard_view()
        action = "Froze" if updated["is_frozen"] else "Unfroze"
        self.notify(f"{action} ACC-{updated['account_id']} (mock).", title="[ ACCOUNT ]")

    def action_show_users_page(self) -> None:
        self.current_page = "users-page"
        self._sync_page_buttons()

    def action_show_suspicious_page(self) -> None:
        if self.permission < 2:
            self.notify("Only admins can open the suspicious activity page.", title="[ ACCESS ]", severity="warning")
            return
        self.current_page = "suspicious-page"
        self._sync_page_buttons()

    def action_create_user(self) -> None:
        self._open_create_user_modal()

    def action_create_account(self) -> None:
        self._open_create_account_modal()

    def action_refresh(self) -> None:
        self._refresh_dashboard_view(notify=True)

    def action_logout(self) -> None:
        delete_token()
        self.app.pop_screen()
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "staff-user-search":
            return
        self.user_search = event.value
        self._refresh_dashboard_view()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "staff-user-table" and event.cursor_row < len(self.filtered_users):
            self.selected_user_id = self.filtered_users[event.cursor_row]["user_id"]
            user_accounts = mock_get_accounts_for_user(self.selected_user_id)
            self.selected_user_account_id = user_accounts[0]["account_id"] if user_accounts else None
            self._render_selected_user()
            self._render_selected_user_accounts()
            return

        if event.data_table.id == "staff-user-accounts-table":
            user_accounts = mock_get_accounts_for_user(self.selected_user_id) if self.selected_user_id is not None else []
            if event.cursor_row < len(user_accounts):
                self.selected_user_account_id = user_accounts[event.cursor_row]["account_id"]
            return

        if event.data_table.id == "staff-suspicious-table":
            suspicious_accounts = mock_get_suspicious_accounts()
            if event.cursor_row < len(suspicious_accounts):
                self.selected_suspicious_account_id = suspicious_accounts[event.cursor_row]["account_id"]
                self._render_suspicious_preview()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "staff-users-page-btn":
            self.action_show_users_page()
        elif button_id == "staff-suspicious-page-btn":
            self.action_show_suspicious_page()
        elif button_id == "staff-create-user-btn":
            self._open_create_user_modal()
        elif button_id == "staff-delete-user-btn":
            self._delete_selected_user()
        elif button_id == "staff-create-account-btn":
            self._open_create_account_modal()
        elif button_id == "staff-close-account-btn":
            self._close_selected_account()
        elif button_id == "staff-freeze-account-btn":
            self._toggle_selected_account_freeze()
        elif button_id in {"staff-users-refresh-btn", "staff-suspicious-refresh-btn"}:
            self.action_refresh()
        elif button_id == "staff-logout-btn":
            self.action_logout()


def get_dashboard_screen_for_permission(permission: int) -> Screen:
    if permission >= 1:
        return StaffDashboardScreen()
    from dashboard import DashboardScreen
    return DashboardScreen()
