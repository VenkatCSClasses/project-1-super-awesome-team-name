import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static, DataTable, Sparkline
from rich.text import Text
from dotenv import load_dotenv

from token_utils import delete_token

load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

    
MOCK_USER = {
    "username": "jsmith",
    "full_name": "John Smith",
    "customer_id": "CUS-00847291",
    "member_since": "2024-03-15",
    "permission": 0,
}

MOCK_ACCOUNTS = [
    {
        "id": "ACCT-1",
        "type": "CHECKING",
        "name": "Primary Checking",
        "balance": 12847.53,
        "status": "ACTIVE",
        "interest_rate": 0.01,
    },
    {
        "id": "ACCT-2",
        "type": "SAVINGS",
        "name": "Emergency Fund",
        "balance": 45230.00,
        "status": "ACTIVE",
        "interest_rate": 4.25,
    },
    {
        "id": "ACCT-3",
        "type": "SAVINGS",
        "name": "Vacation Savings",
        "balance": 3420.75,
        "status": "ACTIVE",
        "interest_rate": 4.25,
    },
]

MOCK_TRANSACTIONS = [
    {"id": "TXN-1", "date": "2026-03-06", "time": "14:32:01", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -89.99, "balance": 12847.53},
    {"id": "TXN-2", "date": "2026-03-06", "time": "09:15:44", "type": "DEPOSIT", "description": "Deposit", "amount": 2847.00, "balance": 12937.52},
    {"id": "TXN-3", "date": "2026-03-05", "time": "18:22:33", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -45.32, "balance": 10090.52},
    {"id": "TXN-4", "date": "2026-03-05", "time": "12:08:19", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -127.84, "balance": 10135.84},
    {"id": "TXN-5", "date": "2026-03-04", "time": "16:45:02", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -15.99, "balance": 10263.68},
    {"id": "TXN-6", "date": "2026-03-04", "time": "11:30:55", "type": "TRANSFER", "description": "To ACC-001", "amount": -500.00, "balance": 10279.67},
    {"id": "TXN-7", "date": "2026-03-03", "time": "08:00:00", "type": "WITHDRAWAL", "description": "Withdrawal", "amount": -142.30,"balance": 10779.67},
    {"id": "TXN-8", "date": "2026-03-02",("time"): "19:44:12","type": "WITHDRAWAL",("description"): "Withdrawal", "amount": -34.50,("balance"): 10921.97},
]

# Sparkline data for account balance history (last 30 days simulated)
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
        status_indicator = "[green]●[/]" if acc["status"] == "ACTIVE" else "[red]●[/]"
        
        yield Static(
            f"{status_indicator} {type_icon} [bold cyan]{acc['name']}[/]\n"
            f"[dim]ID: {acc['id']}[/]  [dim]│[/]  [dim]Type: {acc['type']}[/]\n"
            f"[bold green]${acc['balance']:,.2f}[/]  [dim]APY: {acc['interest_rate']}%[/]",
            classes="account-info"
        )


class StatusBar(Static):
    """System status bar with technical info."""

    def compose(self) -> ComposeResult:
        import datetime
        now = datetime.datetime.now()
        yield Static(
            f"[dim]SYS[/] [green]●[/] ONLINE  "
            f"[dim]│[/]  [dim]API[/] [green]●[/] CONNECTED  "
            f"[dim]│[/]  [dim]SESSION[/] {now.strftime('%H:%M:%S')}  "
            f"[dim]│[/]  [dim]PING[/] [green]12ms[/]"
        )


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
        yield Header()
        
        # Top status bar
        with Container(id="status-bar"):
            yield StatusBar()
        
        # Main dashboard grid
        with Container(id="dashboard-main"):
            # Left panel - User info & Accounts
            with Vertical(id="left-panel"):
                # User info box
                with Container(id="user-info-box"):
                    yield Static("╭─ USER SESSION ─────────────────────────╮", classes="box-top")
                    yield Static(
                        f"  [bold cyan]{MOCK_USER['full_name']}[/] [dim]@{MOCK_USER['username']}[/]\n"
                        f"  [dim]ID:[/] {MOCK_USER['customer_id']}\n"
                        f"  [dim]Member Since:[/] {MOCK_USER['member_since']}\n"
                        f"  [dim]Access Level:[/] [yellow]CUSTOMER[/]",
                        id="user-details"
                    )
                    yield Static("╰────────────────────────────────────────╯", classes="box-bottom")
                
                # Accounts section
                with Container(id="accounts-section"):
                    yield Static("╭─ ACCOUNTS ──────────────────────────────────────────────────╮", classes="box-top")
                    total = sum(acc["balance"] for acc in MOCK_ACCOUNTS)
                    yield Static(f"  [bold]TOTAL BALANCE:[/] [bold green]${total:,.2f}[/]  [dim]│[/]  [dim]{len(MOCK_ACCOUNTS)} accounts[/]", id="total-balance")
                    yield Static("├──────────────────────────────────────────────────────────────┤", classes="box-divider")
                    with Vertical(id="accounts-list"):
                        for acc in MOCK_ACCOUNTS:
                            yield AccountCard(acc, classes="account-card")
                    yield Static("╰──────────────────────────────────────────────────────────────╯", classes="box-bottom")
            
            # Right panel - Transactions & Charts
            with Vertical(id="right-panel"):
                # Balance trend
                with Container(id="trend-box"):
                    yield Static("╭─ 30-DAY BALANCE TREND ─────────────────────────────────────────────────╮", classes="box-top")
                    yield Sparkline(MOCK_BALANCE_HISTORY, summary_function=max, id="balance-sparkline")
                    min_bal = min(MOCK_BALANCE_HISTORY)
                    max_bal = max(MOCK_BALANCE_HISTORY)
                    yield Static(f"  [dim]MIN:[/] [red]${min_bal:,.0f}[/]  [dim]│[/]  [dim]MAX:[/] [green]${max_bal:,.0f}[/]  [dim]│[/]  [dim]CHANGE:[/] [green]+{max_bal - min_bal:,.0f} (+{((max_bal-min_bal)/min_bal)*100:.1f}%)[/]", classes="trend-stats")
                    yield Static("╰───────────────────────────────────────────────────────────────────────────╯", classes="box-bottom")
                
                # Transaction history
                with Container(id="transactions-box"):
                    yield Static("╭─ RECENT TRANSACTIONS ──────────────────────────────────────────────────╮", classes="box-top")
                    yield DataTable(id="transactions-table")
                    yield Static("╰───────────────────────────────────────────────────────────────────────────╯", classes="box-bottom")
        
        # Bottom action bar
        with Horizontal(id="action-bar"):
            yield Button("[ NEW ACCOUNT ]", id="new-account-btn", variant="success")
            yield Button("[ TRANSFER ]", id="transfer-btn", variant="primary")
            yield Button("[ DEPOSIT ]", id="deposit-btn", variant="primary")
            yield Button("[ WITHDRAW ]", id="withdraw-btn", variant="warning")
            yield Button("[ STATEMENTS ]", id="statements-btn", variant="default")
            yield Button("[ LOGOUT ]", id="logout-btn", variant="error")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the transactions table."""
        table = self.query_one("#transactions-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Add columns
        table.add_column("ID", key="id", width=12)
        table.add_column("DATE", key="date", width=12)
        table.add_column("TIME", key="time", width=10)
        table.add_column("TYPE", key="type", width=10)
        table.add_column("DESCRIPTION", key="desc", width=22)
        table.add_column("AMOUNT", key="amount", width=14)
        table.add_column("BALANCE", key="balance", width=14)
        
        for txn in MOCK_TRANSACTIONS:
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "logout-btn":
            self.action_logout()
        elif event.button.id == "new-account-btn":
            self.notify("Account creation coming soon!", title="[ NEW ACCOUNT ]", severity="information")
        elif event.button.id == "transfer-btn":
            self.notify("Transfer feature coming soon!", title="[ TRANSFER ]", severity="information")
        elif event.button.id == "deposit-btn":
            self.notify("Deposit feature coming soon!", title="[ DEPOSIT ]", severity="information")
        elif event.button.id == "withdraw-btn":
            self.notify("Withdraw feature coming soon!", title="[ WITHDRAW ]", severity="information")
        elif event.button.id == "statements-btn":
            self.notify("Statements feature coming soon!", title="[ STATEMENTS ]", severity="information")

    def action_logout(self) -> None:
        """Log out and return to login screen."""
        delete_token()
        self.app.pop_screen()
        self.notify("Session terminated.", title="[ LOGOUT ]")
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())

    def action_new_account(self) -> None:
        """Create new account."""
        self.notify("Account creation coming soon!", title="[ NEW ACCOUNT ]")

    def action_transfer(self) -> None:
        """Transfer funds."""
        self.notify("Transfer feature coming soon!", title="[ TRANSFER ]")

    def action_refresh(self) -> None:
        """Refresh dashboard data."""
        self.notify("Data refreshed.", title="[ REFRESH ]", severity="information")