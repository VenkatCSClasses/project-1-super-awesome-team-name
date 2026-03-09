import os
import sys
from pathlib import Path
import pyfiglet

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, LoadingIndicator, Static, Header, Footer
from dotenv import load_dotenv

from token_utils import save_token

load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

class RegisterScreen(Screen):
    """Register screen with username, password, and email inputs."""

    SUB_TITLE = "Register"
    BINDINGS = [
        Binding("escape", "app.quit", "Quit"),
        Binding("r", "register", "Register"),
        Binding("enter", "login", "Login"),
    ]

    logo = pyfiglet.figlet_format("BankOS")

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="login-container"):
            yield Static(f"BankOS ver{os.getenv('BANK_OS_VERSION', '1.0.1')}", id="title")
            yield Static(self.logo, id="bank-logo")
            yield Static("Register an account", id="subtitle")
            
            with Vertical(id="form"):
                yield Label("Username")
                yield Input(placeholder="Enter your username", id="username")
                yield Label("Password")
                yield Input(placeholder="Enter your password", password=True, id="password")
                yield Label("Confirm Password")
                yield Input(placeholder="Confirm your password", password=True, id="confirm-password")
                
                yield Static("", id="error-message")
                yield LoadingIndicator(id="loading")
                
                with Horizontal(id="buttons"):
                    yield Button("Register", id="register-btn", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        """Focus username input on mount."""
        self.query_one("#username", Input).focus()
        self.query_one("#loading").display = False

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields."""
        if event.input.id == "username":
            self.query_one("#password", Input).focus()
        elif event.input.id == "password":
            self.query_one("#confirm-password", Input).focus()
        elif event.input.id == "confirm-password":
            self.action_register()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "register-btn":
            self.action_register()

    def action_register(self) -> None:
        """Attempt to register."""
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value
        confirm_password = self.query_one("#confirm-password", Input).value

        if not username or not password or not confirm_password:
            self.show_error("Please fill in all fields")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match")
            return

        self.do_register(username, password)


    @work(exclusive=True)
    async def do_register(self, username: str, password: str) -> None:
        """Perform registration request asynchronously."""
        self.set_loading(True)
        self.clear_error()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SERVER_BASE_URL}/register",
                    json={"username": username, "password": password},
                    timeout=10.0,
                )

            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if token:
                    save_token(token)
                    from dashboard import DashboardScreen
                    self.app.push_screen(DashboardScreen())
                else:
                    self.show_error("Invalid response from server")
            elif response.status_code == 401:
                self.show_error("Invalid username or password")
            elif response.status_code == 500:
                self.show_error("Server error. Please try again later.")
            else:
                detail = response.json().get("detail", "Login failed")
                self.show_error(detail)
        except httpx.ConnectError:
            self.show_error("Cannot connect to server. Is it running?")
        except httpx.TimeoutException:
            self.show_error("Request timed out. Please try again.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
        finally:
            self.set_loading(False)


    def show_error(self, message: str) -> None:
        """Display an error message."""
        error_widget = self.query_one("#error-message", Static)
        error_widget.update(f"⚠ {message}")
        error_widget.add_class("visible")

    def clear_error(self) -> None:
        """Clear the error message."""
        error_widget = self.query_one("#error-message", Static)
        error_widget.update("")
        error_widget.remove_class("visible")

    def set_loading(self, loading: bool) -> None:
        """Toggle loading state."""
        self.query_one("#loading").display = loading
        self.query_one("#register-btn", Button).disabled = loading


