import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from checking_account import CheckingAccount
from customer import Customer
from savings_account import SavingsAccount


class Bank:
    SECRET_KEY = os.getenv("SECRET_KEY", "placeholder_secret_key")
    ALGORITHM = "HS256"

    def __init__(self, json_data: dict | None = None, storage_path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent.parent / "database.json"
        self.storage_path = Path(storage_path or os.getenv("DATABASE_JSON_PATH", str(default_path))).resolve()

        self.users: list[Customer] = []
        self.accounts: list[CheckingAccount] = []
        self._next_user_id = 1
        self._next_account_id = 1
        self._password_hasher = PasswordHasher()

        if json_data:
            self._load_from_json_data(json_data)


    @classmethod
    def load_from_file(cls, storage_path: str | Path | None = None) -> "Bank":
        bank = cls(storage_path=storage_path)
        if not bank.storage_path.exists():
            return bank

        try:
            data = json.loads(bank.storage_path.read_text(encoding="utf-8"))
            bank._load_from_json_data(data)
        except (json.JSONDecodeError, OSError):
            pass

        return bank


    def save_to_file(self, storage_path: str | Path | None = None) -> None:
        target = Path(storage_path).resolve() if storage_path else self.storage_path
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target.with_suffix(f"{target.suffix}.tmp")
        temp_path.write_text(json.dumps(self.save_to_json(), indent=2), encoding="utf-8")
        temp_path.replace(target)

    def _load_from_json_data(self, json_data: dict) -> None:
        self.users = []
        self.accounts = []

        for user_record in json_data.get("users", []):
            username = user_record.get("username", user_record.get("name"))
            user_id = user_record.get("id")
            if username is None or user_id is None:
                continue

            hashed_password = user_record.get(
                "hashed_password",
                user_record.get("password", user_record.get("passwd", "")),
            )
            permission = user_record.get("permission", user_record.get("permissions", 0))
            self.users.append(Customer(username, user_id, hashed_password, permission))

        accounts_by_id: dict[int, CheckingAccount] = {}
        for account_record in json_data.get("accounts", []):
            account_id = account_record.get("id")
            if account_id is None:
                continue

            balance = float(account_record.get("balance", 0.0))
            account_type = account_record.get("type", "checking")
            if account_type == "savings":
                account = SavingsAccount(account_id, balance)
            else:
                account = CheckingAccount(account_id, balance)

            account.is_frozen = bool(account_record.get("frozen", False))
            self.accounts.append(account)
            accounts_by_id[account_id] = account

        for user, user_record in zip(self.users, json_data.get("users", [])):
            for account_id in user_record.get("bank_account_ids", []):
                account = accounts_by_id.get(account_id)
                if account:
                    user.register_account(account)

        max_user_id = max((user.get_id() for user in self.users), default=0)
        counter_user_id = int(json_data.get("counters", {}).get("users", 0))
        self._next_user_id = max(max_user_id, counter_user_id) + 1
        max_account_id = max((account.account_num for account in self.accounts), default=0)
        counter_account_id = int(json_data.get("counters", {}).get("accounts", 0))
        self._next_account_id = max(max_account_id, counter_account_id) + 1


    def save_to_json(self) -> dict:
        users = []
        for user in self.users:
            users.append(
                {
                    "id": user.get_id(),
                    "username": user.get_name(),
                    "hashed_password": user.get_passwd(),
                    "permission": self._user_permission(user),
                    "bank_account_ids": [account.account_num for account in user.get_accounts()],
                }
            )

        accounts = []
        for account in self.accounts:
            accounts.append(
                {
                    "id": account.account_num,
                    "balance": account.balance,
                    "frozen": account.is_frozen,
                    "type": "savings" if isinstance(account, SavingsAccount) else "checking",
                    "transactions": [],
                }
            )

        return {
            "users": users,
            "accounts": accounts,
            "counters": {
                "users": self._next_user_id - 1,
                "accounts": self._next_account_id - 1,
            },
        }


    def generate_login_token(self, user_id: int, permission: int) -> str:
        minutes_valid = int(os.getenv("TOKEN_LIFETIME_MINUTES", "60"))
        expire = datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)
        payload = {"user_id": user_id, "permission": permission, "exp": expire}
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)


    def register_user(self, username: str, password: str) -> bool:
        if self.get_user_by_name(username) is not None:
            return False

        user = Customer(
            username,
            self._next_user_id,
            self._password_hasher.hash(password),
            permissions=0,
        )
        self._next_user_id += 1
        self.add_user(user)
        return True


    def login_user(self, username: str, password: str):
        user = self.get_user_by_name(username)
        if user is None:
            return False

        try:
            self._password_hasher.verify(user.get_passwd(), password)
        except (VerifyMismatchError, ValueError, TypeError):
            return False

        return self.generate_login_token(user.get_id(), self._user_permission(user))


    def ensure_root_user(self) -> bool:
        if self.get_user_by_name("root") is not None:
            return False

        user = Customer(
            "root",
            self._next_user_id,
            self._password_hasher.hash("root"),
            permissions=2,
        )
        self._next_user_id += 1
        self.add_user(user)
        return True


    def _user_permission(self, user: Customer) -> int:
        return int(getattr(user, "permissions", 0))


    def get_total_balance(self, user: Customer | None = None) -> float:
        if user is None:
            return sum(account.balance for account in self.accounts)
        return sum(account.balance for account in user.get_accounts())


    def _compound_savings_interest(self) -> None:
        for account in self.get_all_accounts(only_savings=True):
            account.compound_interest()


    def _reset_withdraw_limits(self) -> None:
        for account in self.get_all_accounts(only_savings=True):
            account.reset_withdraw_limit()


    def daily_changes(self) -> None:
        self._compound_savings_interest()
        self._reset_withdraw_limits()


    def add_user(self, user: Customer) -> None:
        if self.get_user_by_id(user.get_id()) is not None:
            raise KeyError(f"User id already exists: {user.get_id()}")
        self.users.append(user)
        self._next_user_id = max(self._next_user_id, user.get_id() + 1)


    def add_account(self, account: CheckingAccount) -> None:
        if any(existing.account_num == account.account_num for existing in self.accounts):
            raise KeyError(f"Account id already exists: {account.account_num}")
        self.accounts.append(account)
        self._next_account_id = max(self._next_account_id, account.account_num + 1)

    def _next_account_num(self) -> int:
        next_id = self._next_account_id
        self._next_account_id += 1
        return next_id


    def create_account_for_user(self, user: Customer, account_type: str = "checking") -> CheckingAccount:
        if account_type == "savings":
            account = SavingsAccount(self._next_account_num(), 0.0)
        else:
            account = CheckingAccount(self._next_account_num(), 0.0)

        self.add_account(account)
        user.register_account(account)
        return account

    
    def get_accounts_for_user(self, user: Customer) -> list[int]:
        return user.get_accounts()



    def get_all_users(self) -> list[Customer]:
        pass


    def get_users(self) -> list[Customer]:
        pass


    def get_all_accounts(self, only_savings: bool = False) -> list[CheckingAccount]:
        pass


    def get_user_by_id(self, user_id: int) -> Customer | None:
        for user in self.users:
            if user.get_id() == user_id:
                return user
        return None


    def get_user_by_name(self, username: str) -> Customer | None:
        for user in self.users:
            if user.get_name() == username:
                return user
        return None


    def get_account(self, account_num: int) -> CheckingAccount:
        pass


    def remove_user(self, identifier) -> Customer:
        pass


    def remove_user_by_id(self, user_id: int) -> Customer:
        pass

    def remove_user_by_name(self, username: str) -> Customer:
        pass

    def remove_account(self, id: int) -> CheckingAccount:
        pass
