import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pyfiglet

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Button, ContentSwitcher, Footer, Header, Input, Label, LoadingIndicator, Static
from dotenv import load_dotenv

from token_utils import get_permissions, save_token

load_dotenv()
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://localhost:8000")


@dataclass(frozen=True)
class AuthFormConfig:
    view_id: str
    username_input_id: str
    password_input_id: str
    confirm_password_input_id: str | None
    error_message_id: str
    loading_id: str
    submit_button_id: str
    switch_button_id: str

    @property
    def focus_widget_ids(self) -> list[str]:
        ids = [self.username_input_id, self.password_input_id]
        if self.confirm_password_input_id:
            ids.append(self.confirm_password_input_id)
        ids.extend([self.submit_button_id, self.switch_button_id])
        return ids


class LoginForm(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Username")
        yield Input(placeholder="Enter your username", id="login-username")
        yield Label("Password")
        yield Input(placeholder="Enter your password", password=True, id="login-password")
        yield Static("", id="login-error-message")
        yield LoadingIndicator(id="login-loading")
        with Horizontal(id="buttons"):
            yield Button("Login", id="login-btn", variant="primary")
            yield Button("Create account", id="go-register-btn")


class RegisterForm(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Username")
        yield Input(placeholder="Choose a username", id="register-username")
        yield Label("Password")
        yield Input(placeholder="Create a password", password=True, id="register-password")
        yield Label("Confirm Password")
        yield Input(placeholder="Confirm password", password=True, id="register-confirm-password")
        yield Static("", id="register-error-message")
        yield LoadingIndicator(id="register-loading")
        with Horizontal(id="buttons"):
            yield Button("Register", id="register-btn", variant="primary")
            yield Button("Back to login", id="go-login-btn")


class LoginScreen(Screen):
    """Auth screen with login/register forms inside a content switcher."""

    SUB_TITLE = "Login"
    BINDINGS = [
        Binding("escape", "app.quit", "Quit"),
        Binding("left,h", "switch_login", "Login", priority=True),
        Binding("right,l", "switch_register", "Register", priority=True),
        Binding("down,j", "focus_next", "Next Field", show=False),
        Binding("up,k", "focus_prev", "Prev Field", show=False),
        Binding("enter", "submit_current", "Submit"),
    ]

    logo = pyfiglet.figlet_format("BankOS")
    _ACTIVE_LOGIN = "login-view"
    _ACTIVE_REGISTER = "register-view"
    _LOGIN_FORM = AuthFormConfig(
        view_id=_ACTIVE_LOGIN,
        username_input_id="login-username",
        password_input_id="login-password",
        confirm_password_input_id=None,
        error_message_id="login-error-message",
        loading_id="login-loading",
        submit_button_id="login-btn",
        switch_button_id="go-register-btn",
    )
    _REGISTER_FORM = AuthFormConfig(
        view_id=_ACTIVE_REGISTER,
        username_input_id="register-username",
        password_input_id="register-password",
        confirm_password_input_id="register-confirm-password",
        error_message_id="register-error-message",
        loading_id="register-loading",
        submit_button_id="register-btn",
        switch_button_id="go-login-btn",
    )
    _FORM_BY_VIEW = {
        _ACTIVE_LOGIN: _LOGIN_FORM,
        _ACTIVE_REGISTER: _REGISTER_FORM,
    }
    _NEXT_INPUT_BY_ID = {
        "login-username": "login-password",
        "register-username": "register-password",
        "register-password": "register-confirm-password",
    }
    _SUBMIT_ACTION_BY_INPUT_ID = {
        "login-password": "login",
        "register-confirm-password": "register",
    }
    _BUTTON_ACTIONS = {
        "switch-login-btn": "switch_login",
        "go-login-btn": "switch_login",
        "switch-register-btn": "switch_register",
        "go-register-btn": "switch_register",
        "login-btn": "login",
        "register-btn": "register",
    }

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="auth-shell"):
            with Horizontal(id="auth-switch-tabs"):
                yield Button("<- Login", id="switch-login-btn", variant="primary")
                yield Button("Register ->", id="switch-register-btn")
            with Container(id="login-container"):
                yield Static(f"BankOS ver{os.getenv('BANK_OS_VERSION', '1.0.1')}", id="title")
                yield Static(self.logo, id="bank-logo")
                yield Static("Use ←/→ to switch between login and register", id="subtitle")

                with ContentSwitcher(initial=self._ACTIVE_LOGIN, id="auth-switcher"):
                    with LoginForm(id=self._ACTIVE_LOGIN, classes="auth-form"):
                        pass
                    with RegisterForm(id=self._ACTIVE_REGISTER, classes="auth-form"):
                        pass

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#login-loading", LoadingIndicator).display = False
        self.query_one("#register-loading", LoadingIndicator).display = False
        self.set_active_view(self._ACTIVE_LOGIN)

    def get_active_view(self) -> str:
        return cast(str, self.query_one("#auth-switcher", ContentSwitcher).current)

    def _active_form_config(self) -> AuthFormConfig:
        return self._FORM_BY_VIEW[self.get_active_view()]

    def set_active_view(self, view: str) -> None:
        switcher = self.query_one("#auth-switcher", ContentSwitcher)
        switcher.current = view
        is_login = view == self._ACTIVE_LOGIN
        self.query_one("#switch-login-btn", Button).variant = "primary" if is_login else "default"
        self.query_one("#switch-register-btn", Button).variant = "primary" if not is_login else "default"
        self.clear_error()
        form = self._FORM_BY_VIEW[view]
        self.query_one(f"#{form.username_input_id}", Input).focus()

    def _focus_order(self) -> list[Input | Button]:
        form = self._active_form_config()
        widgets: list[Input | Button] = []
        for widget_id in form.focus_widget_ids:
            if widget_id.endswith("-btn"):
                widgets.append(self.query_one(f"#{widget_id}", Button))
            else:
                widgets.append(self.query_one(f"#{widget_id}", Input))
        return widgets

    def action_focus_next(self) -> None:
        widgets = self._focus_order()
        if not widgets:
            return
        focused = self.app.focused
        if focused in widgets:
            index = widgets.index(focused)
            widgets[(index + 1) % len(widgets)].focus()
            return
        widgets[0].focus()

    def action_focus_prev(self) -> None:
        widgets = self._focus_order()
        if not widgets:
            return
        focused = self.app.focused
        if focused in widgets:
            index = widgets.index(focused)
            widgets[(index - 1) % len(widgets)].focus()
            return
        widgets[-1].focus()

    def action_switch_login(self) -> None:
        self.sub_title = "Login"
        self.set_active_view(self._ACTIVE_LOGIN)

    def action_switch_register(self) -> None:
        self.sub_title = "Register"
        self.set_active_view(self._ACTIVE_REGISTER)

    def on_key(self, event: Key) -> None:
        """Force global left/right and h/l screen switching regardless of focus."""
        if event.key in ("left", "h"):
            self.action_switch_login()
            event.stop()
        elif event.key in ("right", "l"):
            self.action_switch_register()
            event.stop()

    def action_submit_current(self) -> None:
        if self.get_active_view() == self._ACTIVE_LOGIN:
            self.action_login()
            return
        self.action_register()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        input_id = event.input.id
        if not input_id:
            return

        next_input = self._NEXT_INPUT_BY_ID.get(input_id)
        if next_input:
            self.query_one(f"#{next_input}", Input).focus()
            return

        submit_action = self._SUBMIT_ACTION_BY_INPUT_ID.get(input_id)
        if submit_action == "login":
            self.action_login()
        elif submit_action == "register":
            self.action_register()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if not button_id:
            return

        action = self._BUTTON_ACTIONS.get(button_id)
        if action == "switch_login":
            self.action_switch_login()
        elif action == "switch_register":
            self.action_switch_register()
        elif action == "login":
            self.action_login()
        elif action == "register":
            self.action_register()

    def action_login(self) -> None:
        username = self.query_one(f"#{self._LOGIN_FORM.username_input_id}", Input).value.strip()
        password = self.query_one(f"#{self._LOGIN_FORM.password_input_id}", Input).value

        if not username or not password:
            self.show_error("Please enter both username and password")
            return

        self.do_login(username, password)

    def action_register(self) -> None:
        username = self.query_one(f"#{self._REGISTER_FORM.username_input_id}", Input).value.strip()
        password = self.query_one(f"#{self._REGISTER_FORM.password_input_id}", Input).value
        confirm_password = self.query_one(
            f"#{self._REGISTER_FORM.confirm_password_input_id}",
            Input,
        ).value

        if not username or not password or not confirm_password:
            self.show_error("Please fill in all fields")
            return
        if password != confirm_password:
            self.show_error("Passwords do not match")
            return

        self.do_register(username, password)

    @work(exclusive=True)
    async def do_login(self, username: str, password: str) -> None:
        await self._submit_auth_request(
            endpoint="/login",
            payload={"username": username, "password": password},
            default_error="Login failed",
            unauthorized_error="Invalid username or password",
        )

    @work(exclusive=True)
    async def do_register(self, username: str, password: str) -> None:
        await self._submit_auth_request(
            endpoint="/register",
            payload={"username": username, "password": password},
            default_error="Registration failed",
        )

    async def _submit_auth_request(
        self,
        endpoint: str,
        payload: dict[str, str],
        default_error: str,
        unauthorized_error: str | None = None,
    ) -> None:
        self.set_loading(True)
        self.clear_error()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SERVER_BASE_URL}{endpoint}",
                    json=payload,
                    timeout=10.0,
                )

            if response.status_code == 200:
                self._handle_auth_success(response)
            elif response.status_code == 401 and unauthorized_error:
                self.show_error(unauthorized_error)
            elif response.status_code == 500:
                self.show_error("Server error. Please try again later.")
            else:
                self.show_error(self._response_error_message(response, default_error))
        except httpx.ConnectError:
            self.show_error("Cannot connect to server. Is it running?")
        except httpx.TimeoutException:
            self.show_error("Request timed out. Please try again.")
        except Exception as error:
            self.show_error(f"Error: {error}")
        finally:
            self.set_loading(False)

    def _handle_auth_success(self, response: httpx.Response) -> None:
        data = response.json()
        token = data.get("token")
        if token:
            save_token(token)
            from staff_dashboard import get_dashboard_screen_for_permission

            permission = get_permissions()
            self.app.pop_screen()
            self.app.push_screen(get_dashboard_screen_for_permission(permission))
            return
        self.show_error("Invalid response from server")

    @staticmethod
    def _response_error_message(response: httpx.Response, fallback: str) -> str:
        try:
            payload = response.json()
        except ValueError:
            return fallback
        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str) and detail:
                return detail
        return fallback

    def show_error(self, message: str) -> None:
        form = self._active_form_config()
        error_widget = self.query_one(f"#{form.error_message_id}", Static)
        error_widget.update(f"⚠ {message}")
        error_widget.add_class("visible")

    def clear_error(self) -> None:
        for form in (self._LOGIN_FORM, self._REGISTER_FORM):
            error_widget = self.query_one(f"#{form.error_message_id}", Static)
            error_widget.update("")
            error_widget.remove_class("visible")

    def set_loading(self, loading: bool) -> None:
        active_form = self._active_form_config()
        for form in (self._LOGIN_FORM, self._REGISTER_FORM):
            self.query_one(f"#{form.loading_id}", LoadingIndicator).display = loading and form == active_form
            self.query_one(f"#{form.submit_button_id}", Button).disabled = loading
