from __future__ import annotations

import os

import httpx
import jwt
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, ContentSwitcher, DataTable, Footer, Header, Input, Label, Select, Static
from dotenv import load_dotenv

from token_utils import delete_token, load_token

load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")


def _permission_label(permission: int) -> str:
    return {0: "CUSTOMER", 1: "TELLER", 2: "ADMIN"}.get(permission, "UNKNOWN")


def _permission_color(permission: int) -> str:
    return {0: "yellow", 1: "cyan", 2: "red"}.get(permission, "white")


def _fallback_current_token() -> dict:
    token = load_token()
    if not token:
        return {"username": "unknown", "user_id": "unknown", "permission": -1}
    payload = jwt.decode(token, options={"verify_signature": False})
    return {
        "username": payload.get("sub", payload.get("username", "unknown")),
        "user_id": str(payload.get("user_id", "unknown")),
        "permission": payload.get("permission", -1),
    }


class StaffApiError(Exception):
    def __init__(self, message: str, *, session_expired: bool = False) -> None:
        super().__init__(message)
        self.session_expired = session_expired


def _response_error_message(response: httpx.Response, fallback: str) -> str:
    try:
        payload = response.json()
    except ValueError:
        return fallback
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str) and detail:
            return detail
        message = payload.get("message")
        if isinstance(message, str) and message:
            return message
    return fallback


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
                        password=bool(field.get("password", False)),
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


class StaffFocusBox(Container):
    can_focus = True
    BINDINGS = [
        Binding("left,h", "nav_left", show=False),
        Binding("right,l", "nav_right", show=False),
        Binding("up,k", "nav_up", show=False),
        Binding("down,j", "nav_down", show=False),
    ]

    def action_nav_left(self) -> None:
        self.screen.handle_focus_box_nav(self.id or "", "left")

    def action_nav_right(self) -> None:
        self.screen.handle_focus_box_nav(self.id or "", "right")

    def action_nav_up(self) -> None:
        self.screen.handle_focus_box_nav(self.id or "", "up")

    def action_nav_down(self) -> None:
        self.screen.handle_focus_box_nav(self.id or "", "down")


class StaffNavTable(DataTable):
    BINDINGS = [
        Binding("left,h", "nav_left", show=False),
        Binding("right,l", "nav_right", show=False),
        Binding("up,k", "nav_up", show=False),
        Binding("down,j", "nav_down", show=False),
    ]

    def action_nav_left(self) -> None:
        if self.cursor_coordinate.column > 0:
            self.action_cursor_left()
            return
        self.screen.handle_staff_table_boundary(self.id or "", "left")

    def action_nav_right(self) -> None:
        if self.cursor_coordinate.column < len(self.columns) - 1:
            self.action_cursor_right()
            return
        self.screen.handle_staff_table_boundary(self.id or "", "right")

    def action_nav_up(self) -> None:
        if self.row_count > 0 and self.cursor_coordinate.row > 0:
            self.action_cursor_up()
            return
        self.screen.handle_staff_table_boundary(self.id or "", "up")

    def action_nav_down(self) -> None:
        if self.row_count > 0 and self.cursor_coordinate.row < self.row_count - 1:
            self.action_cursor_down()
            return
        self.screen.handle_staff_table_boundary(self.id or "", "down")


class StaffSearchInput(Input):
    BINDINGS = [
        Binding("up", "nav_up", show=False),
        Binding("down", "nav_down", show=False),
    ]

    def action_nav_up(self) -> None:
        self.screen.focus_current_page_button()

    def action_nav_down(self) -> None:
        self.screen.focus_user_table()


class UserDirectoryBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("USER DIRECTORY", classes="box-top")
        yield Horizontal(
            Static("Search >", classes="staff-search-prefix"),
            StaffSearchInput(placeholder="username, id, role, or status", id="staff-user-search"),
            id="staff-user-search-row",
        )
        yield Static("", id="staff-user-status")
        yield StaffNavTable(id="staff-user-table")


class SelectedUserBox(StaffFocusBox):
    def compose(self) -> ComposeResult:
        yield Static("SELECTED USER", classes="box-top")
        yield Static("", id="staff-user-preview")


class SelectedUserAccountsBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("SELECTED USER ACCOUNTS", classes="box-top")
        yield Static("", id="staff-user-accounts-status")
        yield StaffNavTable(id="staff-user-accounts-table")


class SuspiciousAccountsBox(Container):
    def compose(self) -> ComposeResult:
        yield Static("SUSPICIOUS ACTIVITY", classes="box-top")
        yield Static("", id="staff-suspicious-status")
        yield StaffNavTable(id="staff-suspicious-table")


class SuspiciousPreviewBox(StaffFocusBox):
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
        Binding("space", "toggle_selected_account_freeze", "Freeze / Unfreeze", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.user = _fallback_current_token()
        self.permission = self.user.get("permission", -1)
        self.current_page = "users-page"
        self.user_search = ""
        self.users_data: list[dict] = []
        self.filtered_users: list[dict] = []
        self.accounts_data: list[dict] = []
        self.suspicious_accounts_data: list[dict] = []
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
                    Button("FREEZE / UNFREEZE", id="staff-user-freeze-account-btn", variant="warning", disabled=self.permission < 2),
                    Button("REFRESH", id="staff-users-refresh-btn", variant="primary"),
                    Static("", classes="staff-actions-spacer"),
                    Button("LOGOUT", id="staff-users-logout-btn", variant="error"),
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
                    Static("", classes="staff-actions-spacer"),
                    Button("LOGOUT", id="staff-suspicious-logout-btn", variant="error"),
                    id="staff-suspicious-actions",
                ),
                id="suspicious-page",
            ),
            initial="users-page",
            id="staff-page-switcher",
        )
        yield Footer()

    def _build_user_info_box(self) -> Container:
        color = _permission_color(self.permission)
        access = _permission_label(self.permission)
        return StaffFocusBox(
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
        return StaffFocusBox(
            Static("OPERATIONS SUMMARY", classes="box-top"),
            Static("", id="staff-summary-content"),
            id="staff-summary-box",
        )

    def on_mount(self) -> None:
        self._refresh_dashboard_view()
        self.call_after_refresh(self.focus_user_table)

    def _page_nav_buttons(self) -> list[Button]:
        return list(self.query("#staff-page-nav Button"))

    def _users_action_buttons(self) -> list[Button]:
        return list(self.query("#staff-users-actions Button"))

    def _suspicious_action_buttons(self) -> list[Button]:
        return list(self.query("#staff-suspicious-actions Button"))

    def _current_action_buttons(self) -> list[Button]:
        return self._users_action_buttons() if self.current_page == "users-page" else self._suspicious_action_buttons()

    def focus_user_info_box(self) -> None:
        self.query_one("#user-info-box", StaffFocusBox).focus()

    def focus_summary_box(self) -> None:
        self.query_one("#staff-summary-box", StaffFocusBox).focus()

    def focus_current_page_button(self) -> None:
        button_id = "#staff-users-page-btn" if self.current_page == "users-page" else "#staff-suspicious-page-btn"
        self.query_one(button_id, Button).focus()

    def focus_page_button(self, index: int) -> None:
        buttons = self._page_nav_buttons()
        if not buttons:
            return
        clamped = max(0, min(index, len(buttons) - 1))
        buttons[clamped].focus()

    def focus_user_search(self) -> None:
        self.query_one("#staff-user-search", StaffSearchInput).focus()

    def focus_user_table(self) -> None:
        self.query_one("#staff-user-table", StaffNavTable).focus()

    def focus_selected_user_box(self) -> None:
        self.query_one("#staff-selected-user-box", SelectedUserBox).focus()

    def focus_user_accounts_table(self) -> None:
        self.query_one("#staff-user-accounts-table", StaffNavTable).focus()

    def focus_suspicious_table(self) -> None:
        self.query_one("#staff-suspicious-table", StaffNavTable).focus()

    def focus_suspicious_preview(self) -> None:
        self.query_one("#staff-suspicious-preview-box", SuspiciousPreviewBox).focus()

    def focus_current_action_button(self, index: int = 0) -> None:
        buttons = self._current_action_buttons()
        if not buttons:
            return
        clamped = max(0, min(index, len(buttons) - 1))
        buttons[clamped].focus()

    def focus_logout_button(self) -> None:
        buttons = self._current_action_buttons()
        if buttons:
            buttons[-1].focus()

    def _focus_users_primary(self) -> None:
        self.focus_user_search()

    def _focus_suspicious_primary(self) -> None:
        self.focus_suspicious_table()

    def handle_focus_box_nav(self, box_id: str, direction: str) -> None:
        if box_id == "user-info-box":
            if direction == "right":
                self.focus_summary_box()
            elif direction == "down":
                self.focus_current_page_button()
            return

        if box_id == "staff-summary-box":
            if direction == "left":
                self.focus_user_info_box()
            elif direction == "down":
                self.focus_current_page_button()
            return

        if box_id == "staff-selected-user-box":
            if direction == "left":
                self.focus_user_table()
            elif direction == "up":
                self.focus_current_page_button()
            elif direction == "down":
                self.focus_user_accounts_table()
            return

        if box_id == "staff-suspicious-preview-box":
            if direction == "left":
                self.focus_suspicious_table()
            elif direction == "up":
                self.focus_current_page_button()
            elif direction == "down":
                self.focus_current_action_button(0)

    def handle_staff_table_boundary(self, table_id: str, direction: str) -> None:
        if table_id == "staff-user-table":
            if direction == "up":
                self.focus_user_search()
            elif direction == "right":
                self.focus_selected_user_box()
            elif direction == "down":
                self.focus_current_action_button(0)
            return

        if table_id == "staff-user-accounts-table":
            if direction == "left":
                self.focus_user_table()
            elif direction == "up":
                self.focus_selected_user_box()
            elif direction == "down":
                self.focus_current_action_button(0)
            return

        if table_id == "staff-suspicious-table":
            if direction == "up":
                self.focus_current_page_button()
            elif direction == "right":
                self.focus_suspicious_preview()
            elif direction == "down":
                self.focus_current_action_button(0)

    def _handle_session_expired(self) -> None:
        delete_token()
        self.notify("Session expired. Please log in again.", title="[ AUTH ]", severity="error")
        self.app.pop_screen()
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

    def _request(self, method: str, path: str, *, json: dict | None = None) -> dict:
        token = load_token()
        if not token:
            raise StaffApiError("Session expired. Please log in again.", session_expired=True)

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.request(method, path, headers=headers, json=json)
            except httpx.RequestError:
                raise StaffApiError("Unable to reach the server")

        if response.status_code == 200:
            try:
                payload = response.json()
            except ValueError:
                return {}
            if isinstance(payload, dict):
                return payload
            raise StaffApiError("Server returned an unexpected response")

        if response.status_code == 401:
            raise StaffApiError(
                _response_error_message(response, "Session expired. Please log in again."),
                session_expired=True,
            )
        if response.status_code == 403:
            raise StaffApiError(_response_error_message(response, "You do not have permission to perform this action"))

        raise StaffApiError(_response_error_message(response, "Request failed"))

    def _accounts_for_user(self, user_id: int | None) -> list[dict]:
        if user_id is None:
            return []
        return [account for account in self.accounts_data if account.get("user_id") == user_id]

    def _suspicious_accounts(self) -> list[dict]:
        return list(self.suspicious_accounts_data)

    def _bank_total_balance(self) -> float:
        return sum(float(account.get("balance", 0.0)) for account in self.accounts_data)

    def _load_data(self) -> None:
        self.user = self._request("GET", "/whoami")
        self.permission = int(self.user.get("permission", -1))
        self.users_data = self._request("GET", "/admin/users").get("users", [])
        self.accounts_data = self._request("GET", "/admin/accounts").get("accounts", [])
        if self.permission >= 2:
            self.suspicious_accounts_data = self._request("GET", "/bank/get-suspicious-accounts").get("suspicious_accounts", [])
        else:
            self.suspicious_accounts_data = []

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
        try:
            self._load_data()
        except StaffApiError as error:
            if error.session_expired:
                self._handle_session_expired()
                return
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.filtered_users = self._apply_user_filter()
        user_ids = {user["user_id"] for user in self.filtered_users}
        suspicious_ids = {account["account_id"] for account in self._suspicious_accounts()}

        if self.selected_user_id not in user_ids:
            self.selected_user_id = self.filtered_users[0]["user_id"] if self.filtered_users else None

        user_accounts = self._accounts_for_user(self.selected_user_id)
        user_account_ids = {account["account_id"] for account in user_accounts}
        if self.selected_user_account_id not in user_account_ids:
            self.selected_user_account_id = user_accounts[0]["account_id"] if user_accounts else None

        if self.selected_suspicious_account_id not in suspicious_ids:
            suspicious_accounts = self._suspicious_accounts()
            self.selected_suspicious_account_id = suspicious_accounts[0]["account_id"] if suspicious_accounts else None

        color = _permission_color(self.permission)
        access = _permission_label(self.permission)
        self.query_one("#user-details", Static).update(
            f"  [dim]Username:[/] [bold {color}]@{self.user['username']}[/]\n"
            f"  [dim]ID:[/] USER-{self.user['user_id']}\n"
            f"  [dim]Access Level:[/] [{color}]{access}[/]"
        )
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
        suspicious_count = len(self._suspicious_accounts())
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
                f"  [dim]Bank Total:[/] [bold green]${self._bank_total_balance():,.2f}[/]",
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

        related_accounts = self._accounts_for_user(selected["user_id"])
        self.query_one("#staff-user-preview", Static).update(
            "\n".join(
                [
                    f"[bold]User:[/] @{selected['username']}",
                    f"[bold]ID:[/] USER-{selected['user_id']}",
                    f"[bold]Role:[/] {_permission_label(selected['permission'])}",
                    f"[bold]Status:[/] {selected['status']}",
                    f"[bold]Accounts:[/] {len(related_accounts)}",
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

        if self.selected_user_id is None:
            self.query_one("#staff-user-accounts-status", Static).update("  [dim]Select a user to view accounts.[/]")
            return

        user_accounts = self._accounts_for_user(self.selected_user_id)
        for index, account in enumerate(user_accounts):
            table.add_row(
                f"ACC-{account['account_id']}",
                account["account_type"],
                f"${account['balance']:,.2f}",
                account["status"],
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

        suspicious_accounts = self._suspicious_accounts()
        for index, account in enumerate(suspicious_accounts):
            table.add_row(
                f"ACC-{account['account_id']}",
                f"@{account['owner']}",
                f"${account['balance']:,.2f}",
                "ACTIVE" if not account["is_frozen"] else "FROZEN",
                account["last_activity"],
            )
            if account["account_id"] == self.selected_suspicious_account_id:
                table.move_cursor(row=index, column=0)

        status_text = (
            f"  [dim]{len(suspicious_accounts)} suspicious account(s) in the queue.[/]"
            if suspicious_accounts
            else "  [dim]No suspicious accounts in the queue.[/]"
        )
        self.query_one("#staff-suspicious-status", Static).update(status_text)

    def _render_suspicious_preview(self) -> None:
        if self.permission < 2:
            self.query_one("#staff-suspicious-preview", Static).update(
                "Admins can review suspicious activity and freeze or unfreeze accounts."
            )
            return

        suspicious_accounts = self._suspicious_accounts()
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
                for account in self._accounts_for_user(self.selected_user_id)
                if account["account_id"] == self.selected_user_account_id
            ),
            None,
        )

    def _selected_suspicious_account(self) -> dict | None:
        return next(
            (
                account
                for account in self._suspicious_accounts()
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
                "Create a new customer, teller, or admin user.",
                [
                    {"id": "new-username", "label": "Username", "kind": "input", "placeholder": "username"},
                    {"id": "new-password", "label": "Password", "kind": "input", "placeholder": "password", "password": True},
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
        if not self.users_data:
            self.notify("No users are available for account creation.", title="[ ACCOUNT ]", severity="warning")
            return
        user_options = [
            (f"@{user['username']} ({_permission_label(user['permission'])})", user["user_id"])
            for user in self.users_data
        ]
        self.app.push_screen(
            StaffActionModal(
                "CREATE ACCOUNT",
                "Create a real bank account for the selected user.",
                [
                    {
                        "id": "account-user-id",
                        "label": "Owner",
                        "kind": "select",
                        "options": user_options,
                        "value": selected_user["user_id"] if selected_user else (user_options[0][1] if user_options else None),
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
            created = self._request(
                "POST",
                "/admin/users",
                json={
                    "username": str(result["new-username"]).strip(),
                    "password": str(result["new-password"]).strip(),
                    "permission": int(result["new-permission"]),
                },
            )["user"]
        except (KeyError, ValueError, StaffApiError) as error:
            if isinstance(error, StaffApiError) and error.session_expired:
                self._handle_session_expired()
                return
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_id = created["user_id"]
        self.current_page = "users-page"
        self._refresh_dashboard_view()
        self.notify(f"Created @{created['username']} with {_permission_label(created['permission'])} access.", title="[ USER ]")

    def _handle_create_account(self, result: dict | None) -> None:
        if result is None:
            return
        try:
            created = self._request(
                "POST",
                "/admin/accounts",
                json={
                    "user_id": int(result["account-user-id"]),
                    "account_type": str(result["account-type"]),
                    "opening_balance": float(str(result["opening-balance"]) or "0"),
                },
            )["account"]
        except (KeyError, ValueError, StaffApiError) as error:
            if isinstance(error, StaffApiError) and error.session_expired:
                self._handle_session_expired()
                return
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_id = created["user_id"]
        self.selected_user_account_id = created["account_id"]
        self.current_page = "users-page"
        self._refresh_dashboard_view()
        self.notify(f"Created ACC-{created['account_id']} for @{created['owner']}.", title="[ ACCOUNT ]")

    def _delete_selected_user(self) -> None:
        if self.permission < 2:
            self.notify("Only admins can delete users.", title="[ USER ]", severity="warning")
            return
        selected = self._selected_user()
        if selected is None:
            self.notify("Select a user first.", title="[ USER ]", severity="warning")
            return
        try:
            deleted = self._request("DELETE", f"/admin/users/{selected['user_id']}")["user"]
        except (KeyError, StaffApiError) as error:
            if isinstance(error, StaffApiError) and error.session_expired:
                self._handle_session_expired()
                return
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_id = None
        self.selected_user_account_id = None
        self._refresh_dashboard_view()
        self.notify(f"Deleted @{deleted['username']}.", title="[ USER ]")

    def _close_selected_account(self) -> None:
        selected = self._selected_user_account()
        if selected is None:
            self.notify("Select an account first.", title="[ ACCOUNT ]", severity="warning")
            return
        try:
            closed = self._request("DELETE", f"/admin/accounts/{selected['account_id']}")["account"]
        except (KeyError, StaffApiError) as error:
            if isinstance(error, StaffApiError) and error.session_expired:
                self._handle_session_expired()
                return
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_account_id = None
        if self.selected_suspicious_account_id == closed["account_id"]:
            self.selected_suspicious_account_id = None
        self._refresh_dashboard_view()
        self.notify(f"Closed ACC-{closed['account_id']}.", title="[ ACCOUNT ]")

    def _toggle_account_freeze(self, account_id: int | None = None) -> None:
        if self.permission < 2:
            self.notify("Only admins can freeze accounts.", title="[ ACCOUNT ]", severity="warning")
            return

        if account_id is None:
            selected = self._selected_suspicious_account()
            if selected is None:
                self.notify("Select an account first.", title="[ ACCOUNT ]", severity="warning")
                return
            account_id = selected["account_id"]

        selected = next((account for account in self.accounts_data if account["account_id"] == account_id), None)
        if selected is None:
            self.notify("Select an account first.", title="[ ACCOUNT ]", severity="warning")
            return
        try:
            freeze_result = self._request("GET", f"/bank/toggle-freeze/{account_id}")
        except (KeyError, StaffApiError) as error:
            if isinstance(error, StaffApiError) and error.session_expired:
                self._handle_session_expired()
                return
            self.notify(str(error), title="[ ERROR ]", severity="error")
            return
        self.selected_user_id = selected["user_id"]
        self.selected_user_account_id = selected["account_id"]
        self.selected_suspicious_account_id = selected["account_id"]
        self._refresh_dashboard_view()
        action = "Froze" if freeze_result["is_frozen"] else "Unfroze"
        self.notify(f"{action} ACC-{selected['account_id']}.", title="[ ACCOUNT ]")

    def action_toggle_selected_account_freeze(self) -> None:
        focused = self.app.focused
        if not isinstance(focused, DataTable):
            return

        if focused.id == "staff-user-accounts-table":
            selected = self._selected_user_account()
            if selected is None:
                self.notify("Select an account first.", title="[ ACCOUNT ]", severity="warning")
                return
            self._toggle_account_freeze(selected["account_id"])
            return

        if focused.id == "staff-suspicious-table":
            self._toggle_account_freeze()

    def on_key(self, event: Key) -> None:
        focused = self.app.focused
        if event.key == "space":
            if isinstance(focused, DataTable) and focused.id in {"staff-user-accounts-table", "staff-suspicious-table"}:
                self.action_toggle_selected_account_freeze()
                event.stop()
            return

        if isinstance(focused, Button):
            if focused.parent is None:
                return

            if focused.parent.id == "staff-page-nav":
                buttons = self._page_nav_buttons()
                if not buttons:
                    return
                index = buttons.index(focused)
                if event.key in ("left", "h"):
                    self.focus_page_button(index - 1)
                    event.stop()
                elif event.key in ("right", "l"):
                    self.focus_page_button(index + 1)
                    event.stop()
                elif event.key in ("up", "k"):
                    self.focus_user_info_box() if index == 0 else self.focus_summary_box()
                    event.stop()
                elif event.key in ("down", "j"):
                    if focused.id == "staff-users-page-btn":
                        self._focus_users_primary()
                    elif focused.id == "staff-suspicious-page-btn":
                        self._focus_suspicious_primary()
                    event.stop()
                return

            if focused.parent.id in {"staff-users-actions", "staff-suspicious-actions"}:
                buttons = self._current_action_buttons()
                if not buttons:
                    return
                index = buttons.index(focused)
                if event.key in ("left", "h"):
                    self.focus_current_action_button(index - 1)
                    event.stop()
                elif event.key in ("right", "l"):
                    self.focus_current_action_button(index + 1)
                    event.stop()
                elif event.key in ("up", "k"):
                    if self.current_page == "users-page":
                        self.focus_user_accounts_table()
                    else:
                        self.focus_suspicious_table()
                    event.stop()
                return

    def action_show_users_page(self) -> None:
        self.current_page = "users-page"
        self._sync_page_buttons()
        self.focus_current_page_button()

    def action_show_suspicious_page(self) -> None:
        if self.permission < 2:
            self.notify("Only admins can open the suspicious activity page.", title="[ ACCESS ]", severity="warning")
            return
        self.current_page = "suspicious-page"
        self._sync_page_buttons()
        self.focus_current_page_button()

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
            user_accounts = self._accounts_for_user(self.selected_user_id)
            self.selected_user_account_id = user_accounts[0]["account_id"] if user_accounts else None
            self._render_selected_user()
            self._render_selected_user_accounts()
            return

        if event.data_table.id == "staff-user-accounts-table":
            user_accounts = self._accounts_for_user(self.selected_user_id)
            if event.cursor_row < len(user_accounts):
                self.selected_user_account_id = user_accounts[event.cursor_row]["account_id"]
            return

        if event.data_table.id == "staff-suspicious-table":
            suspicious_accounts = self._suspicious_accounts()
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
        elif button_id == "staff-user-freeze-account-btn":
            selected = self._selected_user_account()
            self._toggle_account_freeze(selected["account_id"] if selected else None)
        elif button_id == "staff-freeze-account-btn":
            self._toggle_account_freeze()
        elif button_id in {"staff-users-refresh-btn", "staff-suspicious-refresh-btn"}:
            self.action_refresh()
        elif button_id in {"staff-users-logout-btn", "staff-suspicious-logout-btn"}:
            self.action_logout()


def get_dashboard_screen_for_permission(permission: int) -> Screen:
    if permission >= 1:
        return StaffDashboardScreen()
    from dashboard import DashboardScreen
    return DashboardScreen()
