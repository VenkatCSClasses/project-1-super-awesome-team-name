import os
import sys
from pathlib import Path
from server_ping_utils import server_running
from login_screen import LoginScreen
from deposit_modal import DepositModal
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


MOCK_ACCOUNTS = [
    {
        "id": "1",
        "type": "CHECKING",
        "balance": 12847.53,
        "interest_rate": 0.01,
    },
    {
        "id": "2",
        "type": "SAVINGS",
        "balance": 45230.00,
        "interest_rate": 4.25,
    },
    {
        "id": "3",
        "type": "SAVINGS",
        "balance": 3420.75,
        "interest_rate": 4.25,
    },
]

MOCK_TRANSACTIONS = [
    {"id": "1", "date": "2026-03-06", "time": "14:32:01", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -89.99, "balance": 12847.53},
    {"id": "2", "date": "2026-03-06", "time": "09:15:44", "type": "DEPOSIT", "description": "Deposit", "amount": 2847.00, "balance": 12937.52},
    {"id": "3", "date": "2026-03-05", "time": "18:22:33", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -45.32, "balance": 10090.52},
    {"id": "4", "date": "2026-03-05", "time": "12:08:19", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -127.84, "balance": 10135.84},
    {"id": "5", "date": "2026-03-04", "time": "16:45:02", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -15.99, "balance": 10263.68},
    {"id": "6", "date": "2026-03-04", "time": "11:30:55", "type": "TRANSFER", "description": "To ACC-001", "amount": -500.00, "balance": 10279.67},
    {"id": "7", "date": "2026-03-03", "time": "08:00:00", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -142.30,"balance": 10779.67},
    {"id": "8", "date": "2026-03-02", "time": "19:44:12","type": "WITHDRAWAL", "description": "Withdrawal", "amount": -34.50,"balance": 10921.97},
]

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
        type_icon = "█▀▀" if acc["type"] == "CHECKING" else "█▄▄"
        
        yield Static(
            f"{type_icon} [bold]{acc['type']} Account[/]\n"
            f"[dim]ID: ACC-{acc['id']}[/]  [dim]│[/]  [dim]Type: {acc['type']}[/]\n"
            f"[bold green]${acc['balance']:,.2f}[/]  [dim]Interest: {acc['interest_rate']}%[/]",
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
        if self.time_since_last_ping > 0:
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
        yield Static("╭─ USER SESSION ─────────────────────────╮", classes="box-top")

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
        yield Static("╰────────────────────────────────────────╯", classes="box-bottom")

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
        yield Static("╭─ ACCOUNTS ──────────────────────────────────────────────────╮", classes="box-top")
        total = sum(acc["balance"] for acc in self.accounts)
        yield Static(
            f"  [bold]TOTAL BALANCE:[/] [bold green]${total:,.2f}[/]  [dim]│[/]  [dim]{len(self.accounts)} accounts[/]",
            id="total-balance"
        )
        yield Static("├──────────────────────────────────────────────────────────────┤", classes="box-divider")
        yield AccountsList(self.accounts, id="accounts-list")
        yield Static("╰──────────────────────────────────────────────────────────────╯", classes="box-bottom")


class AccountsList(Vertical):
    """Vertical list of account cards."""

    def __init__(self, accounts: list, **kwargs):
        super().__init__(**kwargs)
        self.accounts = accounts

    def compose(self) -> ComposeResult:
        for acc in self.accounts:
            yield AccountCard(acc, classes="account-card")


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

    def compose(self) -> ComposeResult:
        yield Static("╭─ TRANSACTION BALANCE TREND ─────────────────────────────────────────────╮", classes="box-top")
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
            classes="trend-stats"
        )
        yield Static("╰───────────────────────────────────────────────────────────────────────────╯", classes="box-bottom")

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
        yield Static("╭─ RECENT TRANSACTIONS ──────────────────────────────────────────────────╮", classes="box-top")
        yield TransactionsTable(id="transactions-table")
        yield Static("╰───────────────────────────────────────────────────────────────────────────╯", classes="box-bottom")


class ActionBar(Horizontal):
    """Bottom action bar with buttons."""

    def compose(self) -> ComposeResult:
        yield Button("[ NEW ACCOUNT ]", id="new-account-btn", variant="success")
        yield Button("[ TRANSFER ]", id="transfer-btn", variant="primary")
        yield Button("[ DEPOSIT ]", id="deposit-btn", variant="primary")
        yield Button("[ WITHDRAW ]", id="withdraw-btn", variant="warning")
        yield Button("[ FREEZE ACCOUNTS ]", id="freeze-accounts-btn", variant="error")
        yield Button("[ LOGOUT ]", id="logout-btn", variant="error")



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

    def compose(self) -> ComposeResult:
        try:
            user = self.get_user_info()
        except PermissionError:
            self.handle_session_expired()
            return
        except Exception:
            self.app.notify("Unable to load user info.", title="[ ERROR ]", severity="error")
            return
        accounts = self.get_accounts()
        transactions = self.get_transactions()
        balance_history = self.build_balance_history(accounts, transactions)

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
            self.focus_action_button(0)

    def set_selected_account(self, selected_card: AccountCard, announce: bool = True) -> None:
        for card in self._account_cards():
            card.remove_class("selected")
        selected_card.add_class("selected")
        if announce:
            self.notify(
                f"Selected ACC-{selected_card.account.get('id', 'unknown')}",
                title="[ ACCOUNT ]",
                timeout=1.2,
            )

    def handle_session_expired(self) -> None:
        """Clear session token and send user to login screen."""
        delete_token()
        self.app.notify("Session expired. Please log in again.", title="[ AUTH ]", severity="error")
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

    def get_user_info(self) -> dict:
        """Fetch user info from server"""
        token = load_token()
        if not token:
            raise PermissionError("Missing auth token")

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
                if response.status_code in (401, 403):
                    raise PermissionError("Auth token expired or invalid")
                print(f"Failed to fetch user info: {response.status_code}")
            except httpx.RequestError as e:
                print(f"Error connecting to server: {e}")
        raise Exception("Unable to fetch user info from server")

    def get_accounts(self) -> list:
        """Fetch accounts from server"""
        return MOCK_ACCOUNTS

    def get_transactions(self) -> list:
        """Fetch transactions from server"""
        token = load_token()
        if not token:
            raise PermissionError("Missing auth token")

        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(base_url=SERVER_BASE_URL, timeout=5) as client:
            try:
                response = client.get("/bank/view_my_transaction_history/", headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    return response_data.get("transactions", [])
                if response.status_code in (401, 403):
                    raise PermissionError("Auth token expired or invalid")
                print(f"Failed to fetch user info: {response.status_code}")
            except httpx.RequestError as e:
                print(f"Error connecting to server: {e}")
        raise Exception("Unable to fetch transaction info from server")
        

    def build_balance_history(self, accounts: list, transactions: list) -> list[float]:
        """Build balance history from transactions in chronological order."""
        if transactions:
            ordered_transactions = sorted(
                transactions,
                key=lambda txn: f"{txn.get('date', '')} {txn.get('time', '')}"
            )
            history = [txn["balance"] for txn in ordered_transactions if "balance" in txn]
            if history:
                return history

        if accounts:
            total = sum(acc["balance"] for acc in accounts)
            return [total]

        return [0]

    def generate_transaction_table(self, transactions: list) -> None:
        """Helper to populate the transactions data table."""
        table = self.query_one("#transactions-table", DataTable)

        # Rebuild columns on refresh to avoid duplicate column definitions.
        table.clear(columns=True)
        # Add columns
        table.add_column("ID", key="id", width=12)
        table.add_column("DATE", key="date", width=12)
        table.add_column("TIME", key="time", width=10)
        table.add_column("TYPE", key="type", width=10)
        table.add_column("DESCRIPTION", key="desc", width=22)
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

    def on_mount(self) -> None:
        transactions = self.get_transactions()
        self.generate_transaction_table(transactions)
        cards = self._account_cards()
        if cards:
            self.set_selected_account(cards[0], announce=False)
        self.call_after_refresh(self.focus_accounts_list)

    def on_key(self, event) -> None:
        """Arrow/vim movement while focused on action buttons."""
        focused = self.app.focused
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
            self.app.push_screen(CreateBankAccountModal())
        elif event.button.id == "transfer-btn":
            self.notify("Transfer feature coming soon!", title="[ TRANSFER ]", severity="information")
        elif event.button.id == "deposit-btn":
            self.app.push_screen(DepositModal())
        elif event.button.id == "withdraw-btn":
            self.app.push_screen(WithdrawModal())
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
        self.app.push_screen(CreateBankAccountModal())

    def action_transfer(self) -> None:
        """Transfer funds."""
        self.notify("Transfer feature coming soon!", title="[ TRANSFER ]")

    def action_refresh(self) -> None:
        """Refresh dashboard data."""
        transactions = self.get_transactions()
        self.generate_transaction_table(transactions)
        self.notify("Data refreshed.", title="[ REFRESH ]", severity="information")
