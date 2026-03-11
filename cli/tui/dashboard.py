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
from textual.widgets import Button, Footer, Header, Static, DataTable, Sparkline
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

MOCK_BALANCE_HISTORY = [
    8500, 8450, 8600, 8580, 9200, 9180, 9150, 9300, 9280, 9500,
    9480, 9700, 9650, 10200, 10180, 10500, 10480, 10450, 10800, 10750,
    10900, 10850, 11200, 11500, 11480, 12000, 12200, 12500, 12900, 12847,
]


class AccountCard(Static):
    """A card widget displaying account info."""

    def __init__(self, account: dict, **kwargs):
        super().__init__(**kwargs)
        self.account = account

    def compose(self) -> ComposeResult:
        acc = self.account
        type_icon = "█▀▀" if acc["type"] == "CHECKING" else "█▄▄"
        
        yield Static(
            f"[dim]ID: ACC-{acc['id']}[/]  [dim]│[/]  [dim]Type: {acc['type']}[/]\n"
            f"[bold green]${acc['balance']:,.2f}[/]  [dim]Interest: {acc['interest_rate']}%[/]",
            classes="account-info"
        )


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


class BalanceTrendBox(Container):
    """30-day balance trend chart."""

    def __init__(self, balance_history: list, **kwargs):
        super().__init__(**kwargs)
        self.balance_history = balance_history

    def compose(self) -> ComposeResult:
        yield Static("╭─ 30-DAY BALANCE TREND ─────────────────────────────────────────────────╮", classes="box-top")
        yield Sparkline(self.balance_history, summary_function=max, id="balance-sparkline")
        min_bal = min(self.balance_history)
        max_bal = max(self.balance_history)
        change_pct = ((max_bal - min_bal) / min_bal) * 100
        yield Static(
            f"  [dim]MIN:[/] [red]${min_bal:,.0f}[/]  [dim]│[/]  "
            f"[dim]MAX:[/] [green]${max_bal:,.0f}[/]  [dim]│[/]  "
            f"[dim]CHANGE:[/] [green]+{max_bal - min_bal:,.0f} (+{change_pct:.1f}%)[/]",
            classes="trend-stats"
        )
        yield Static("╰───────────────────────────────────────────────────────────────────────────╯", classes="box-bottom")


class TransactionsBox(Container):
    """Recent transactions box with data table."""

    def compose(self) -> ComposeResult:
        yield Static("╭─ RECENT TRANSACTIONS ──────────────────────────────────────────────────╮", classes="box-top")
        yield DataTable(id="transactions-table")
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
        return MOCK_TRANSACTIONS

    def build_balance_history(self, accounts: list, transactions: list) -> list[float]:
        """Build trend data from loaded account and transaction data."""
        if transactions:
            return [txn["balance"] for txn in transactions][-30:]

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
