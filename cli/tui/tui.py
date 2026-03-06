import sys
from pathlib import Path

# Add parent directory to path to import token_utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import App
from textual.binding import Binding

from token_utils import load_token, get_permissions

from login_screen import LoginScreen
from dashboard import DashboardScreen


class BankApp(App):
    """Main banking TUI application."""

    CSS = """
    Screen {
        align: center middle;
    }

    #login-container, #dashboard-container {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        border-title-color: $primary;
    }

    #bank-logo {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        text-opacity: 100%;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $text;
        padding-bottom: 0;
    }

    #subtitle {
        width: 100%;
        content-align: center middle;
        color: $text-muted;
        padding-bottom: 1;
    }

    #role-display {
        width: 100%;
        content-align: center middle;
        color: $success;
        padding: 1;
    }

    #form, #menu {
        width: 100%;
        height: auto;
        padding: 0 1;
    }

    #form Label {
        padding-top: 1;
        padding-bottom: 0;
        color: $text;
    }

    #form Input {
        width: 100%;
        margin-bottom: 0;
    }

    #form Input:focus {
        border: tall $primary;
    }

    #error-message {
        width: 100%;
        height: auto;
        min-height: 0;
        color: $error;
        text-align: center;
        padding: 0;
        margin: 0;
    }

    #error-message.visible {
        min-height: 2;
        padding: 1 0;
    }

    #loading {
        width: 100%;
        height: 3;
        content-align: center middle;
    }

    #buttons {
        width: 100%;
        height: auto;
        align: center middle;
        padding-top: 1;
    }

    #buttons Button {
        margin: 0 1;
    }

    #menu Button {
        width: 100%;
        margin: 1 0;
    }

    Button {
        min-width: 16;
    }
    """

    TITLE = "BankOS Terminal"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Check if already logged in on startup."""
        token = load_token()
        if token and get_permissions() >= 0:
            self.push_screen(DashboardScreen())
        else:
            self.push_screen(LoginScreen())


if __name__ == "__main__":
    app = BankApp()
    app.run()