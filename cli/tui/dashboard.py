import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from dotenv import load_dotenv

from token_utils import delete_token, get_permissions
load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")


class DashboardScreen(Screen):
    """Main dashboard after successful login."""
    SUB_TITLE = "Dashboard"

    BINDINGS = [
        Binding("q", "logout", "Logout"),
        Binding("escape", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="dashboard-container"):
            yield Static("Dashboard", id="title")
            
            permission = get_permissions()
            role = "Customer"
            if permission == 1:
                role = "Teller"
            elif permission == 2:
                role = "Admin"
            
            yield Static(f"Logged in as: {role}", id="role-display")
            
            with Vertical(id="menu"):
                yield Button("View Account", id="view-account", variant="primary")
                if permission >= 1:
                    yield Button("Teller Operations", id="teller-ops", variant="default")
                if permission >= 2:
                    yield Button("Admin Panel", id="admin-panel", variant="warning")
                yield Button("Logout", id="logout-btn", variant="error")
        yield Footer()


    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "logout-btn":
            self.action_logout()
        elif event.button.id == "view-account":
            self.notify("Account view coming soon!", title="Info")
        elif event.button.id == "teller-ops":
            self.notify("Teller operations coming soon!", title="Info")
        elif event.button.id == "admin-panel":
            self.notify("Admin panel coming soon!", title="Info")


    def action_logout(self) -> None:
        """Log out and return to login screen."""
        delete_token()
        self.app.pop_screen()
        self.notify("Logged out successfully!", title="Goodbye")
        from login_screen import LoginScreen
        self.app.push_screen(LoginScreen())