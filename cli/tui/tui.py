import sys
import subprocess
from pathlib import Path
import time
from server_ping_utils import server_running


# Add parent directory to path to import token_utils
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server" / "src")) 


from textual.app import App
from textual.binding import Binding

from token_utils import load_token, get_permissions

from login_screen import LoginScreen
from register import RegisterScreen
import requests
from dotenv import load_dotenv
import os
from dashboard import DashboardScreen


class BankApp(App):
    """Main banking TUI application."""

    CSS = """
    Screen {
        background: #0a0a0a;
    }

    Header {
        background: #1a1a2e;
        color: #00ff88;
    }

    Footer {
        background: #1a1a2e;
    }

    LoginScreen {
        align: center middle;
    }

    RegisterScreen {
        align: center middle;
    }

    #login-container {
        width: 60;
        height: auto;
        padding: 1 2;
        background: #0d0d0d;
        border: heavy #00ff88;
    }

    #bank-logo {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: #00ff88;
        text-opacity: 100%;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: #00ff88;
        padding-bottom: 0;
    }

    #subtitle {
        width: 100%;
        content-align: center middle;
        color: #666666;
        padding-bottom: 1;
    }

    #role-display {
        width: 100%;
        content-align: center middle;
        color: #00ff88;
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
        color: #888888;
    }

    #form Input {
        width: 100%;
        margin-bottom: 0;
        background: #1a1a1a;
        border: tall #333333;
        color: #00ff88;
    }

    #form Input:focus {
        border: tall #00ff88;
    }

    #error-message {
        width: 100%;
        height: auto;
        min-height: 0;
        color: #ff4444;
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
        background: #1a1a2e;
        border: tall #00ff88;
        color: #00ff88;
    }

    Button:hover {
        background: #00ff88;
        color: #0a0a0a;
    }

    Button.-primary {
        background: #0d4d2e;
        border: tall #00ff88;
    }

    Button.-success {
        background: #0d4d2e;
        border: tall #00ff88;
    }

    Button.-warning {
        background: #4d3d0d;
        border: tall #ffaa00;
        color: #ffaa00;
    }

    Button.-error {
        background: #4d0d0d;
        border: tall #ff4444;
        color: #ff4444;
    }

    #login-btn {
        width: 100%;
        align: center middle;
    }
    #register-btn {
        width: 100%;
        align: center middle;
    }

    /* ============================================
       DASHBOARD SCREEN STYLES - btop aesthetic
       ============================================ */
    #status-bar {
        width: 100%;
        height: 1;
        background: #0d0d0d;
        padding: 0 1;
        dock: top;
    }

    #status-bar Static {
        width: 100%;
        color: #888888;
    }

    #dashboard-main {
        width: 100%;
        height: 1fr;
        layout: horizontal;
        padding: 0;
        max-height: 100%;
    }

    DashboardScreen {
        layout: vertical;
    }

    #left-panel {
        width: 45;
        height: 100%;
        padding: 0 1;
    }

    #right-panel {
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }

    /* User info box */
    #user-info-box {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    #user-details {
        padding: 0 0;
        color: #cccccc;
    }

    /* Box styling */
    .box-top, .box-bottom, .box-divider {
        color: #00ff88;
        width: 100%;
        height: 1;
    }

    /* Accounts section */
    #accounts-section {
        width: 100%;
        height: auto;
    }

    #total-balance {
        padding: 0 0;
        height: 1;
    }

    #accounts-list {
        width: 100%;
        height: auto;
        padding: 0;
    }

    .account-card {
        width: 100%;
        height: auto;
        padding: 1 2;
        margin: 0;
        background: #0d0d0d;
    }

    .account-card:hover {
        background: #1a1a2e;
    }

    .account-info {
        width: 100%;
    }

    /* Trend box */
    #trend-box {
        width: 100%;
        height: 14;
        margin-bottom: 1;
    }

    #balance-line-chart {
        width: 100%;
        height: 6;
        padding: 0 2;
        color: #00ff88;
    }

    .trend-stats {
        padding: 0 0;
        height: 1;
    }

    /* Transactions box */
    #transactions-box {
        width: 100%;
        height: 1fr;
    }

    #transactions-table {
        width: 100%;
        height: 1fr;
        background: #0a0a0a;
        margin: 0 1;
    }

    DataTable {
        background: #0a0a0a;
    }

    DataTable > .datatable--header {
        background: #1a1a2e;
        color: #00ff88;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: #1a3a2e;
    }

    DataTable > .datatable--odd-row {
        background: #0d0d0d;
    }

    DataTable > .datatable--even-row {
        background: #0a0a0a;
    }

    /* Action bar */
    #action-bar {
        width: 100%;
        height: 3;
        padding: 0 1;
        background: #0d0d0d;
        align: center middle;
        border-top: solid #333333;
    }

    #action-bar Button {
        min-width: 14;
        height: 3;
        margin: 0 1;
    }

    ModalScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    .modal-container {
        width: 64;
        height: auto;
        padding: 1 2;
        background: #0d0d0d;
        border: thick #00ff88;
    }

    .modal-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: #00ff88;
        margin-bottom: 1;
    }

    .modal-subtitle {
        width: 100%;
        content-align: center middle;
        color: #7a7a7a;
        margin-bottom: 1;
    }

    .modal-label {
        color: #cfcfcf;
        margin-top: 1;
    }

    .modal-hint {
        color: #8a8a8a;
        margin-top: 1;
        margin-bottom: 1;
    }

    .modal-feedback {
        min-height: 1;
    }

    .modal-container Input {
        width: 100%;
        background: #121212;
        border: tall #333333;
        color: #00ff88;
    }

    .modal-container Input:focus {
        border: tall #00ff88;
    }

    #account-type-options {
        margin: 1 0;
        border: none;
    }

    #modal-actions {
        margin-top: 1;
        width: 100%;
        height: 3;
        align: right middle;
    }

    #modal-actions Button {
        margin-left: 1;
    }

    .freeze-modal-container {
        width: 110;
        height: 34;
    }

    #freeze-controls {
        width: 100%;
        height: 3;
        align: left middle;
    }

    #freeze-controls Button {
        min-width: 14;
        margin-right: 1;
    }

    #freeze-controls Checkbox {
        margin-left: 2;
        color: #cccccc;
    }

    #freeze-search-row {
        width: 100%;
        height: 3;
        align: left middle;
        margin-bottom: 1;
    }

    .freeze-search-prefix {
        width: 10;
        color: #00ff88;
        text-style: bold;
    }

    #freeze-search-input {
        width: 1fr;
    }

    #freeze-main {
        width: 100%;
        height: 1fr;
    }

    .freeze-left-panel {
        width: 60%;
        height: 100%;
        margin-right: 1;
    }

    .freeze-right-panel {
        width: 40%;
        height: 100%;
    }

    #freeze-table {
        width: 100%;
        height: 1fr;
        border: solid #2a2a2a;
    }

    #freeze-preview {
        width: 100%;
        height: 1fr;
        padding: 1;
        background: #101010;
        border: solid #2a2a2a;
    }

    #freeze-feedback {
        color: #8a8a8a;
        margin-top: 1;
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




def main():
    server_process = None
    if not server_running():
        server_script = Path(__file__).parent.parent.parent / "server" / "src" / "server.py"
        server_process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)
    try:
        app = BankApp()
        app.run()
    finally:
        if server_process:
            server_process.terminate()


if __name__ == "__main__":
    main()
