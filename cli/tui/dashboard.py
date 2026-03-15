import os
import sys
from pathlib import Path
from server_ping_utils import server_running
from login_screen import LoginScreen
from deposit_modal import DepositModal
from transfer_modal import TransferModal
from withdraw_modal import WithdrawModal
from freeze_accounts_modal import FreezeAccountsModal

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import datetime
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static, DataTable
from rich.text import Text
from dotenv import load_dotenv
from create_bank_account_modal import CreateBankAccountModal

from token_utils import delete_token, load_token

load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")


class AccountCard(Static):
    """A card widget displaying account info."""
    can_focus = True
    BINDINGS = [
        Binding("up,k", "focus_prev_account", show=False),
        Binding("down,j", "focus_next_account", show=False),
        Binding("left,h", "focus_left_group", show=False),
        Binding("right,l", "focus_right_group", show=False),
        Binding("enter,space", "select_account", show=False),
    ]

    def __init__(self, account: dict, **kwargs):
        super().__init__(**kwargs)
        self.account = account

    def compose(self) -> ComposeResult:
        acc = self.account
        account_type = acc.get("account_type", "UNKNOWN").upper()
        type_icon = "█▀▀" if account_type == "CHECKING" else "█▄▄"
        
        yield Static(
            f"{type_icon} [bold]{account_type} Account[/]\n"
            f"[dim]ID: ACC-{acc['account_id']}[/]  [dim]│[/]  [dim]Type: {account_type}[/]\n"
            f"[bold green]${acc['balance']:,.2f}[/]  [dim]Frozen: {acc['is_frozen']}%[/]",
            classes="account-info"
        )

    def action_focus_prev_account(self) -> None:
        self.screen.focus_previous_account(self)

    def action_focus_next_account(self) -> None:
        self.screen.focus_next_account(self)

    def action_focus_left_group(self) -> None:
        return

    def action_focus_right_group(self) -> None:
        self.screen.focus_transactions_table()

    def action_select_account(self) -> None:
        self.screen.set_selected_account(self)

    def on_click(self, event) -> None:
        self.focus()
        self.action_select_account()


class StatusBar(Static):
    """System status bar with technical info."""

    time_since_last_ping = 0
    def compose(self) -> ComposeResult:
        yield Static("", id="status-text")

    def render_status(self, time: datetime.datetime, server_status: bool) -> Text:
        """Helper to format the status string."""
        server_indicator = "[green]●[/] Connected" if server_status else "[red]●[/] Disconnected"
        return Text.from_markup(
            f"[dim]│[/]  [dim]SERVER[/] {server_indicator}  "
            f"[dim]│[/]  [dim]TIME[/] {time.strftime('%H:%M:%S')}  "
        )

    def on_mount(self) -> None:
        # Initial update
        self.update_bar()
        self.set_interval(1, self.update_bar)

    def update_bar(self) -> None:
        server_status = True
        if self.time_since_last_ping == 30:
            self.time_since_last_ping = 0
        if self.time_since_last_ping > 30:
            if server_running():
                server_status = True
            else:
                server_status = False
        self.time_since_last_ping += 1
        now = datetime.datetime.now()
        self.query_one("#status-text", Static).update(self.render_status(now, server_status))

class UserInfoBox(Container):
    """User session information box."""
    can_focus = True
    BINDINGS = [
        Binding("left,h", "focus_left", show=False),
        Binding("right,l", "focus_right", show=False),
        Binding("up,k", "focus_up", show=False),
        Binding("down,j", "focus_down", show=False),
    ]

    def __init__(self, user: dict, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    def compose(self) -> ComposeResult:
        yield Static("USER SESSION", classes="box-top")

        permission = self.user.get("permission", 0)
        match permission:
            case 0:
                access_level, color = "CUSTOMER", "yellow"
            case 1:
                access_level, color = "TELLER", "cyan"
            case 2:
                access_level, color = "ADMIN", "red"
            case _:
                access_level, color = "UNKNOWN", "dim"

        yield Static(
            f"  [dim]Username:[/] [bold {color}]@{self.user['username']}[/]\n"
            f"  [dim]ID:[/] USER-{self.user['user_id']}\n"
            f"  [dim]Access Level:[/] [{color}]{access_level}[/]",
            id="user-details"
        )

    def action_focus_left(self) -> None:
        return

    def action_focus_right(self) -> None:
        self.screen.focus_trend_box()

    def action_focus_up(self) -> None:
        return

    def action_focus_down(self) -> None:
        self.screen.focus_accounts_list()


class AccountsSection(Container):
    """Accounts list section."""

    def __init__(self, accounts: list, **kwargs):
        super().__init__(**kwargs)
        self.accounts = accounts

    def compose(self) -> ComposeResult:
        yield Static("ACCOUNTS", classes="box-top")
        total = sum(acc["balance"] for acc in self.accounts)
        yield Static(
            f"  [bold]TOTAL BALANCE:[/] [bold green]${total:,.2f}[/]  [dim]│[/]  [dim]{len(self.accounts)} accounts[/]",
            id="total-balance"
        )
        yield AccountsList(self.accounts, id="accounts-list")
        yield Button("CREATE NEW ACCOUNT", id="accounts-new-account-btn", variant="success")


class AccountsList(Vertical):
    """Vertical list of account cards."""

    def __init__(self, accounts: list, **kwargs):
        super().__init__(**kwargs)
        self.accounts = accounts

    def _build_children(self) -> list[Static]:
        if not self.accounts:
            return [
                Static(
                    "  [dim]You have no accounts yet. Create one to get started.[/]",
                )
            ]
        return [AccountCard(acc, classes="account-card") for acc in self.accounts]

    def compose(self) -> ComposeResult:
        yield from self._build_children()

    def refresh_accounts(self, accounts: list) -> None:
        """Rebuild the rendered account cards without replacing the list widget."""
        self.accounts = accounts
        self.remove_children()
        self.mount(*self._build_children())


class TransactionsTable(DataTable):
    """Transaction table with boundary-aware cross-widget navigation."""
    BINDINGS = [
        Binding("left,h", "nav_left", show=False),
        Binding("right,l", "nav_right", show=False),
        Binding("up,k", "nav_up", show=False),
        Binding("down,j", "nav_down", show=False),
    ]

    def action_nav_left(self) -> None:
        if len(self.columns) > 0 and self.cursor_coordinate.column > 0:
            self.action_cursor_left()
            return
        self.screen.focus_accounts_list()

    def action_nav_right(self) -> None:
        if len(self.columns) > 0 and self.cursor_coordinate.column < len(self.columns) - 1:
            self.action_cursor_right()
            return

    def action_nav_up(self) -> None:
        if self.row_count > 0 and self.cursor_coordinate.row > 0:
            self.action_cursor_up()
            return
        self.screen.focus_trend_box()

    def action_nav_down(self) -> None:
        if self.row_count > 0 and self.cursor_coordinate.row < self.row_count - 1:
            self.action_cursor_down()
            return
        self.screen.focus_action_button(2)


class BalanceTrendBox(Container):
    """Balance trend chart based on transaction history."""
    can_focus = True
    BINDINGS = [
        Binding("left,h", "focus_left", show=False),
        Binding("right,l", "focus_right", show=False),
        Binding("up,k", "focus_up", show=False),
        Binding("down,j", "focus_down", show=False),
    ]

    def __init__(self, balance_history: list, **kwargs):
        super().__init__(**kwargs)
        self.balance_history = balance_history

    @staticmethod
    def _resample(values: list[float], target_count: int) -> list[float]:
        """Linearly resample values to a fixed number of points."""
        if not values:
            return [0.0]
        if len(values) == 1 or target_count <= 1:
            return [values[0]] * max(target_count, 1)

        result = []
        max_index = len(values) - 1
        for i in range(target_count):
            pos = (i / (target_count - 1)) * max_index
            left = int(pos)
            right = min(left + 1, max_index)
            weight = pos - left
            point = values[left] * (1 - weight) + values[right] * weight
            result.append(point)
        return result

    def render_line_chart(self, width: int = 64, height: int = 6) -> str:
        """Render a multiline line chart so the trend box uses vertical space."""
        samples = self._resample(self.balance_history, width)
        low = min(samples)
        high = max(samples)
        if high == low:
            return "\n".join((" " * width) for _ in range(height - 1)) + f"\n{'─' * width}"

        rows = [[" " for _ in range(width)] for _ in range(height)]

        def y_for(value: float) -> int:
            normalized = (value - low) / (high - low)
            return (height - 1) - round(normalized * (height - 1))

        y_points = [y_for(value) for value in samples]

        for x in range(width):
            y = y_points[x]
            rows[y][x] = "●"
            if x == 0:
                continue
            prev_y = y_points[x - 1]
            step = 1 if y > prev_y else -1
            for mid_y in range(prev_y + step, y, step):
                rows[mid_y][x] = "│"
            if prev_y < y:
                rows[prev_y][x] = "╮"
                rows[y][x] = "╰"
            elif prev_y > y:
                rows[prev_y][x] = "╯"
                rows[y][x] = "╭"
            else:
                rows[y][x] = "─"

        return "\n".join("".join(row) for row in rows)

    def update_chart(self) -> None:
        """Render chart content to fill the available chart widget space."""
        chart_widget = self.query_one("#balance-line-chart", Static)
        width = chart_widget.size.width
        height = chart_widget.size.height
        if width <= 0:
            width = 68
        if height <= 0:
            height = 6
        chart_widget.update(f"[green]{self.render_line_chart(width=width, height=height)}[/]")

    def update_balance_history(self, balance_history: list[float]) -> None:
        """Replace the chart data and refresh the rendered stats."""
        self.balance_history = balance_history or [0]
        min_bal = min(self.balance_history)
        max_bal = max(self.balance_history)
        start_bal = self.balance_history[0]
        end_bal = self.balance_history[-1]
        change = end_bal - start_bal
        change_pct = (change / start_bal) * 100 if start_bal else 0
        change_color = "green" if change >= 0 else "red"
        self.query_one("#trend-stats", Static).update(
            f"  [dim]MIN:[/] [red]${min_bal:,.0f}[/]  [dim]│[/]  "
            f"[dim]MAX:[/] [green]${max_bal:,.0f}[/]  [dim]│[/]  "
            f"[dim]CHANGE:[/] [{change_color}]{change:+,.0f} ({change_pct:+.1f}%)[/]"
        )
        self.update_chart()

    def compose(self) -> ComposeResult:
        yield Static("TRANSACTION BALANCE TREND", classes="box-top")
        yield Static("", id="balance-line-chart")
        min_bal = min(self.balance_history)
        max_bal = max(self.balance_history)
        start_bal = self.balance_history[0]
        end_bal = self.balance_history[-1]
        change = end_bal - start_bal
        change_pct = (change / start_bal) * 100 if start_bal else 0
        change_color = "green" if change >= 0 else "red"
        yield Static(
            f"  [dim]MIN:[/] [red]${min_bal:,.0f}[/]  [dim]│[/]  "
            f"[dim]MAX:[/] [green]${max_bal:,.0f}[/]  [dim]│[/]  "
            f"[dim]CHANGE:[/] [{change_color}]{change:+,.0f} ({change_pct:+.1f}%)[/]",
            classes="trend-stats",
            id="trend-stats",
        )

    def on_mount(self) -> None:
        self.call_after_refresh(self.update_chart)

    def on_resize(self, event) -> None:
        self.update_chart()

    def action_focus_left(self) -> None:
        self.screen.focus_user_box()

    def action_focus_right(self) -> None:
        return

    def action_focus_up(self) -> None:
        return

    def action_focus_down(self) -> None:
        self.screen.focus_transactions_table()


class TransactionsBox(Container):
    """Recent transactions box with data table."""

    def compose(self) -> ComposeResult:
        yield Static("RECENT TRANSACTIONS", classes="box-top")
        yield Static("", id="transactions-status")
        yield TransactionsTable(id="transactions-table")


class ActionBar(Horizontal):
    """Bottom action bar with buttons."""

    def compose(self) -> ComposeResult:
        yield Button("NEW ACCOUNT", id="new-account-btn", variant="success")
        yield Button("TRANSFER", id="transfer-btn", variant="primary")
        yield Button("DEPOSIT", id="deposit-btn", variant="primary")
        yield Button("WITHDRAW", id="withdraw-btn", variant="warning")
        yield Button("LOGOUT", id="logout-btn", variant="error")



class DashboardScreen(Screen):
    """Main dashboard after successful login."""

    SUB_TITLE = "Dashboard"
    
    BINDINGS = [
        Binding("q", "logout", "Logout"),
        Binding("escape", "app.quit", "Quit"),
        Binding("n", "new_account", "New Account"),
        Binding("t", "transfer", "Transfer"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.accounts_data: list[dict] = []
        self.selected_account_id: int | None = None
        self.preferred_selected_account_id: int | None = None
        self.transactions_error_message = ""

    def compose(self) -> ComposeResult:
        try:
            user = self.get_user_info()
        except Exception:
            self.app.notify("Unable to load user info.", title="[ ERROR ]", severity="error")
            user = None
        if user is None:
            user = {"username": "unknown", "user_id": "unknown", "permission": -1}

        accounts = self.get_accounts() or []
        self.accounts_data = accounts
        selected_account = next(
            (
                account
                for account in accounts
                if account["account_id"] == self.preferred_selected_account_id
            ),
            accounts[0] if accounts else None,
        )
        self.selected_account_id = selected_account["account_id"] if selected_account else None
        transactions = self.get_transactions(self.selected_account_id) or []
        balance_history = self.build_balance_history(selected_account, transactions)

        yield Header()
        yield Container(StatusBar(), id="status-bar")
        yield Container(
            Vertical(
                UserInfoBox(user, id="user-info-box"),
                AccountsSection(accounts, id="accounts-section"),
                id="left-panel"
            ),
            Vertical(
                BalanceTrendBox(balance_history, id="trend-box"),
                TransactionsBox(id="transactions-box"),
                id="right-panel"
            ),
            id="dashboard-main"
        )
        yield ActionBar(id="action-bar")
        yield Footer()

    def _action_buttons(self) -> list[Button]:
        return list(self.query("#action-bar Button"))

    def _account_cards(self) -> list[AccountCard]:
        return list(self.query("#accounts-list AccountCard"))

    def focus_user_box(self) -> None:
        self.query_one("#user-info-box", UserInfoBox).focus()

    def focus_accounts_list(self) -> None:
        cards = self._account_cards()
        if not cards:
            self.focus_accounts_new_account_button()
            return
        selected = next((card for card in cards if "selected" in card.classes), cards[0])
        selected.focus()

    def focus_trend_box(self) -> None:
        self.query_one("#trend-box", BalanceTrendBox).focus()

    def focus_transactions_table(self) -> None:
        self.query_one("#transactions-table", TransactionsTable).focus()

    def focus_action_button(self, index: int = 0) -> None:
        buttons = self._action_buttons()
        if not buttons:
            return
        clamped = max(0, min(index, len(buttons) - 1))
        buttons[clamped].focus()

    def focus_accounts_new_account_button(self) -> None:
        self.query_one("#accounts-new-account-btn", Button).focus()

    def focus_previous_account(self, current: AccountCard) -> None:
        cards = self._account_cards()
        if not cards:
            return
        try:
            index = cards.index(current)
        except ValueError:
            self.focus_accounts_list()
            return
        if index > 0:
            cards[index - 1].focus()
        else:
            self.focus_user_box()

    def focus_next_account(self, current: AccountCard) -> None:
        cards = self._account_cards()
        if not cards:
            return
        try:
            index = cards.index(current)
        except ValueError:
            self.focus_accounts_list()
            return
        if index < len(cards) - 1:
            cards[index + 1].focus()
        else:
            self.focus_accounts_new_account_button()

    def set_selected_account(self, selected_card: AccountCard, announce: bool = True) -> None:
        for card in self._account_cards():
            card.remove_class("selected")
        selected_card.add_class("selected")
        self.selected_account_id = selected_card.account.get("account_id")
        self.preferred_selected_account_id = self.selected_account_id
        self.refresh_selected_account_data()
        if announce:
            self.notify(
                f"Selected ACC-{selected_card.account.get('account_id', 'unknown')}",
                title="[ ACCOUNT ]",
                timeout=1.2,
            )

    def handle_session_expired(self) -> None:
        """Clear session token and send user to login screen."""
        delete_token()
        self.app.notify("Session expired. Please log in again.", title="[ AUTH ]", severity="error")
        from login_screen import LoginScreen
        self.app.pop_screen()
        self.app.push_screen(LoginScreen())

    def get_user_info(self) -> dict:
        """Fetch user info from server"""
        token = load_token()
        if not token:
            self.handle_session_expired()
            return None

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.get("/whoami", headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    return {
                        "username": response_data.get("username", "unknown"),
                        "user_id": str(response_data.get("user_id", "unknown")),
                        "permission": response_data.get("permission", -1),
                    }
                if response.status_code in (401, 403, 404):
                    self.handle_session_expired()
                    return None
                print(f"Failed to fetch user info: {response.status_code}")
            except httpx.RequestError as e:
                print(f"Error connecting to server: {e}")
        raise Exception("Unable to fetch user info from server")

    def get_accounts(self) -> list:
        """Fetch transactions from server"""
        token = load_token()
        if not token:
            self.handle_session_expired()
            return None

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.get("/bank/get_all_bank_accounts", headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    return self._normalize_accounts(response_data.get("accounts", []))
                if response.status_code in (401, 403, 404):
                    self.handle_session_expired()
                    return None
                print(f"Failed to fetch user info: {response.status_code}")
            except httpx.RequestError as e:
                print(f"Error connecting to server: {e}")
        return []

    def get_transactions(self, account_id: int | None) -> list:
        """Fetch transactions for the selected account from server."""
        if account_id is None:
            return []

        token = load_token()
        if not token:
            self.handle_session_expired()
            return None

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.get(f"/bank/view_transaction_history/{account_id}", headers=headers)
                if response.status_code == 200:
                    self.transactions_error_message = ""
                    response_data = response.json()
                    return self._normalize_transactions(response_data.get("transactions", []))
                if response.status_code in (401, 403, 404):
                    self.handle_session_expired()
                    return None
                self.transactions_error_message = (
                    f"Unable to load transaction history for ACC-{account_id} right now."
                )
                print(f"Failed to fetch transaction info: {response.status_code}")
            except httpx.RequestError as e:
                self.transactions_error_message = (
                    f"Unable to reach the server for ACC-{account_id} transaction history."
                )
                print(f"Error connecting to server: {e}")
        return []
        

    def build_balance_history(self, account: dict | None, transactions: list) -> list[float]:
        """Build balance history from transactions in chronological order."""
        if transactions:
            ordered_transactions = sorted(
                transactions,
                key=lambda txn: txn.get("sort_key", ""),
            )
            history = [txn["balance"] for txn in ordered_transactions if "balance" in txn]
            if history:
                return history

        if account:
            return [account["balance"]]

        return [0]

    def _normalize_accounts(self, accounts: object) -> list[dict]:
        """Return a safe list of account dicts for dashboard rendering."""
        if not isinstance(accounts, list):
            return []
        normalized: list[dict] = []
        for account in accounts:
            if not isinstance(account, dict):
                continue
            if not {"account_id", "account_type", "balance", "is_frozen"} <= account.keys():
                continue
            normalized.append(account)
        return normalized

    def _normalize_transactions(self, transactions: object) -> list[dict]:
        """Convert API responses into rows the TUI can render."""
        if isinstance(transactions, dict):
            raw_transactions = transactions.values()
        elif isinstance(transactions, list):
            raw_transactions = transactions
        else:
            return []

        normalized: list[dict] = []
        for transaction in raw_transactions:
            if not isinstance(transaction, dict):
                continue

            timestamp = (
                transaction.get("timestamp")
                or transaction.get("datetime_str")
                or transaction.get("datetime")
                or ""
            )
            date_str = transaction.get("date", "")
            time_str = transaction.get("time", "")
            sort_key = ""
            if timestamp:
                try:
                    parsed = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    date_str = parsed.strftime("%Y-%m-%d")
                    time_str = parsed.strftime("%H:%M:%S")
                    sort_key = parsed.isoformat()
                except ValueError:
                    sort_key = str(timestamp)
            else:
                sort_key = f"{date_str} {time_str}".strip()

            transaction_type = self._format_transaction_type(
                transaction.get("type", transaction.get("transaction_type"))
            )
            amount = float(transaction.get("amount", 0.0))
            balance = float(transaction.get("balance", transaction.get("post_balance", 0.0)))
            description = transaction.get("description") or self._build_transaction_description(
                transaction_type,
                amount,
                transaction.get("transfer_account_id"),
            )
            normalized.append(
                {
                    "id": str(
                        transaction.get(
                            "absolute_transaction_id",
                            transaction.get("id", transaction.get("relative_transaction_id", "")),
                        )
                    ),
                    "date": date_str or "--",
                    "time": time_str or "--",
                    "type": transaction_type,
                    "description": description,
                    "amount": amount,
                    "balance": balance,
                    "sort_key": sort_key,
                }
            )

        return sorted(normalized, key=lambda txn: txn["sort_key"])

    def _format_transaction_type(self, raw_type: object) -> str:
        """Normalize server transaction types into readable labels."""
        type_map = {
            1: "WITHDRAWAL",
            2: "DEPOSIT",
            3: "TRANSFER",
            4: "TRANSFER",
            5: "NEW ACCOUNT",
            6: "INTEREST",
            "WITHDRAW": "WITHDRAWAL",
            "DEPOSIT": "DEPOSIT",
            "TRANSFER_WITHDRAW": "TRANSFER",
            "TRANSFER_DEPOSIT": "TRANSFER",
            "NEW_ACCOUNT": "NEW ACCOUNT",
            "INTEREST": "INTEREST",
        }
        if isinstance(raw_type, dict):
            raw_type = raw_type.get("value", raw_type.get("name"))
        return type_map.get(raw_type, str(raw_type or "UNKNOWN").replace("_", " ").upper())

    def _build_transaction_description(self, transaction_type: str, amount: float, transfer_account_id: object) -> str:
        """Fallback description when the API doesn't send one."""
        amount_text = f"${abs(amount):,.2f}"
        if transaction_type == "WITHDRAWAL":
            return f"Withdrawal of {amount_text}"
        if transaction_type == "DEPOSIT":
            return f"Deposit of {amount_text}"
        if transaction_type == "TRANSFER":
            if transfer_account_id is not None:
                direction = "from" if amount > 0 else "to"
                return f"Transfer {direction} ACC-{transfer_account_id} of {amount_text}"
            return f"Transfer of {amount_text}"
        if transaction_type == "NEW ACCOUNT":
            return f"New account created with balance {amount_text}"
        if transaction_type == "INTEREST":
            return f"Collected interest amount of {amount_text}"
        return transaction_type.title()

    def update_transactions_status(self, message: str) -> None:
        """Update the help text above the transaction history table."""
        self.query_one("#transactions-status", Static).update(message)

    def refresh_selected_account_data(self) -> None:
        """Reload the table and trend box for the currently selected account."""
        selected_account = next(
            (account for account in self.accounts_data if account["account_id"] == self.selected_account_id),
            None,
        )
        if selected_account is None:
            self.generate_transaction_table([])
            self.query_one("#trend-box", BalanceTrendBox).update_balance_history([0])
            self.update_transactions_status(
                "  [dim]You have no accounts yet. Create one to view transaction history.[/]"
            )
            return

        transactions = self.get_transactions(self.selected_account_id)
        if transactions is None:
            return

        self.generate_transaction_table(transactions)
        self.query_one("#trend-box", BalanceTrendBox).update_balance_history(
            self.build_balance_history(selected_account, transactions)
        )
        if self.transactions_error_message:
            self.update_transactions_status(f"  [red]{self.transactions_error_message}[/]")
            return
        if transactions:
            self.update_transactions_status(
                f"  [dim]Showing transaction history for ACC-{self.selected_account_id}.[/]"
            )
        else:
            self.update_transactions_status(
                f"  [dim]ACC-{self.selected_account_id} has no transactions yet.[/]"
            )

    def generate_transaction_table(self, transactions: list) -> None:
        """Helper to populate the transactions data table."""
        table = self.query("#transactions-table").first()
        if not isinstance(table, DataTable):
            return

        # Rebuild columns on refresh to avoid duplicate column definitions.
        table.clear(columns=True)
        # Add columns
        table.add_column("ID", key="id", width=10)
        table.add_column("DATE", key="date", width=10)
        table.add_column("TIME", key="time", width=8)
        table.add_column("TYPE", key="type", width=15)
        table.add_column("DESCRIPTION", key="desc", width=60)
        table.add_column("AMOUNT", key="amount", width=14)
        table.add_column("BALANCE", key="balance", width=14)
        
        for txn in transactions:
            # Color code the type
            type_color = {
                "DEPOSIT": "green",
                "WITHDRAWAL": "red",
                "TRANSFER": "yellow",
            }.get(txn["type"], "white")
            
            # Color code the amount
            amount_str = f"${txn['amount']:+,.2f}"
            amount_color = "green" if txn["amount"] > 0 else "red"
            
            table.add_row(
                txn["id"],
                txn["date"],
                txn["time"],
                Text(txn["type"], style=type_color),
                txn["description"],
                Text(amount_str, style=amount_color),
                f"${txn['balance']:,.2f}",
            )

    def _populate_dashboard(self) -> None:
        cards = self._account_cards()
        if cards:
            selected_card = next(
                (
                    card
                    for card in cards
                    if card.account.get("account_id") == self.selected_account_id
                ),
                cards[0],
            )
            for card in cards:
                card.remove_class("selected")
            selected_card.add_class("selected")
            self.selected_account_id = selected_card.account.get("account_id")
            self.preferred_selected_account_id = self.selected_account_id
            self.refresh_selected_account_data()
            self.focus_accounts_list()
            return

        self.refresh_selected_account_data()
        self.focus_accounts_new_account_button()

    def on_mount(self) -> None:
        self.call_after_refresh(self._populate_dashboard)

    def on_key(self, event) -> None:
        """Arrow/vim movement while focused on button groups."""
        focused = self.app.focused
        if isinstance(focused, Button) and focused.id == "accounts-new-account-btn":
            if event.key in ("up", "k"):
                cards = self._account_cards()
                if cards:
                    cards[-1].focus()
                event.stop()
            elif event.key in ("right", "l"):
                self.focus_transactions_table()
                event.stop()
            elif event.key in ("down", "j"):
                self.focus_action_button(0)
                event.stop()
            return

        if not isinstance(focused, Button) or focused.parent is None or focused.parent.id != "action-bar":
            return

        buttons = self._action_buttons()
        if not buttons:
            return
        index = buttons.index(focused)

        if event.key in ("left", "h"):
            self.focus_action_button(index - 1)
            event.stop()
        elif event.key in ("right", "l"):
            self.focus_action_button(index + 1)
            event.stop()
        elif event.key in ("up", "k"):
            self.focus_transactions_table()
            event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "logout-btn":
            self.action_logout()
        elif event.button.id == "new-account-btn":
            self.app.push_screen(CreateBankAccountModal(), self._handle_account_change)
        elif event.button.id == "accounts-new-account-btn":
            self.app.push_screen(CreateBankAccountModal(), self._handle_account_change)
        elif event.button.id == "transfer-btn":
            self.app.push_screen(TransferModal(), self._handle_account_change)
        elif event.button.id == "deposit-btn":
            self.app.push_screen(DepositModal(), self._handle_account_change)
        elif event.button.id == "withdraw-btn":
            self.app.push_screen(WithdrawModal(), self._handle_account_change)
        elif event.button.id == "freeze-accounts-btn":
            self.app.push_screen(FreezeAccountsModal())

    def action_logout(self) -> None:
        """Log out and return to login screen."""
        delete_token()
        self.app.pop_screen()
        self.notify("Session terminated.", title="[ LOGOUT ]")
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

    def action_new_account(self) -> None:
        """Create new account."""
        self.app.push_screen(CreateBankAccountModal(), self._handle_account_change)

    def action_transfer(self) -> None:
        """Transfer funds."""
        self.app.push_screen(TransferModal(), self._handle_account_change)

    def _handle_account_change(self, result) -> None:
        """Refresh dashboard state after a successful account action."""
        if result is None:
            return

        if isinstance(result, dict):
            self.preferred_selected_account_id = (
                result.get("account_id")
                or result.get("from_account_id")
                or self.selected_account_id
            )
        else:
            self.preferred_selected_account_id = self.selected_account_id
        self._refresh_dashboard_view()

    def _rebuild_accounts_section(self) -> None:
        """Refresh the mounted accounts pane so cards and totals reflect current data."""
        accounts_section = self.query_one("#accounts-section", AccountsSection)
        accounts_section.accounts = self.accounts_data
        total_balance = sum(account["balance"] for account in self.accounts_data)
        self.query_one("#total-balance", Static).update(
            f"  [bold]TOTAL BALANCE:[/] [bold green]${total_balance:,.2f}[/]  "
            f"[dim]│[/]  [dim]{len(self.accounts_data)} accounts[/]"
        )
        existing_list = self.query_one("#accounts-list", AccountsList)
        existing_list.refresh_accounts(self.accounts_data)

    def _refresh_dashboard_view(self, notify: bool = False) -> None:
        """Refresh mounted dashboard widgets from current server state."""
        self.accounts_data = self.get_accounts() or []
        account_ids = {account["account_id"] for account in self.accounts_data}

        if not self.accounts_data:
            self.selected_account_id = None
        elif self.preferred_selected_account_id in account_ids:
            self.selected_account_id = self.preferred_selected_account_id
        elif self.selected_account_id in account_ids:
            self.selected_account_id = self.selected_account_id
        else:
            self.selected_account_id = self.accounts_data[0]["account_id"]

        self._rebuild_accounts_section()
        self.call_after_refresh(self._populate_dashboard)
        if notify:
            self.notify("Data refreshed.", title="[ REFRESH ]", severity="information")

    def action_refresh(self) -> None:
        """Refresh dashboard data."""
        self._refresh_dashboard_view(notify=True)
