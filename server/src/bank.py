import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from customer import Customer
from savings_account import SavingsAccount
from transaction import Transaction 
from checking_account import CheckingAccount


class Bank:
    """
    A class used to represent an entire functioning bank. Can be saved and pulled to/from json file.

    Attributes:
        users (dict[int, Customer]): Dictionary of users that belong to the bank, key is user ID.
        accounts (dict[int, CheckingAccount]): Dictionary of bank accounts that belong to the bank, key is account ID.
        _next_user_id (int): Next absolute user ID that can be used for a new user.
        _next_account_id (int): Next absolute account ID that can be used for a new account.
        _next_transaction_id (int): Next absolute transaction ID that can be used for a new transaction.
        _password_hasher (PasswordHasher): Set hash method that is used for hashing/unhashing passwords.
        
    Database Helpers:
        SECRET_KEY (str): Secret key given to allow for login tokens to be created.
        ALGORITHM (str): Hashing algorithm helping with login tokens.
        default_path (Path): Base default path of where the json database lives.
        storage_path (Path): Path of where the json should actually be stored at.
    """


    SECRET_KEY = os.getenv("SECRET_KEY", "placeholder_secret_key")
    ALGORITHM = "HS256"

    def __init__(self, json_data: dict | None = None, storage_path: str | Path | None = None) -> None:
        """
        Initializes the Bank object with optional parameters to pass in already pre-existing json data.
        Sets default and storage paths to potential json database files.
        Loads json data into the object if file is passed in.
        Otherwise, sets attributes to default values (either empty dicts or initial IDs of 1).

        Args:
            json_data (dict | None): Dictionary that holds json data to be loaded into the Bank object.
                Defaults to None.
            storage_path (str | Path | None): Path that leads to the place to store json data in.
                Defaults to None.
        """
        default_path = Path(__file__).resolve().parent.parent / "database.json"
        self.storage_path = Path(storage_path or os.getenv("DATABASE_JSON_PATH", str(default_path))).resolve()

        self.users: dict[int, Customer] = {}
        self.accounts: dict[int, Customer] = {}
        self._next_user_id = 1
        self._next_account_id = 1
        self._next_transaction_id = 1
        self._password_hasher = PasswordHasher()

        if json_data:
            self._load_from_json_data(json_data)


    @classmethod
    def load_from_file(cls, storage_path: str | Path | None = None) -> "Bank":
        """
        Initializes generic bank status based on information in file/bank, returning a Bank object.
        Is a generic class method, which can be called without an object, onto the whole class.
        
        Args:
            storage_path (str | Path | None): Path that leads to the place to store json data in.
                Defaults to None.

        Returns:
            Bank: New bank object that holds the information loaded in from the json file.
        """

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
        """
        Saves all data in Bank to the json file.

        Args:
            storage_path (str | Path | None): Path that leads to the place to store json data in.
                Defaults to None.
        """
        target = Path(storage_path).resolve() if storage_path else self.storage_path
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target.with_suffix(f"{target.suffix}.tmp")
        temp_path.write_text(json.dumps(self.save_to_json(), indent=2), encoding="utf-8")
        temp_path.replace(target)


    def _load_from_json_data(self, json_data: dict) -> None:
        """
        Loads data from the json file into the bank object, populating each attribute.
        
        Args: 
            json_data (dict): Data of each attribute stored in a dictionary parsed from json.
        """
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
                account = SavingsAccount(account_id, self, balance)
            else:
                account = CheckingAccount(account_id, self, balance)

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
        max_account_id = max((account.account_id for account in self.accounts), default=0)
        counter_account_id = int(json_data.get("counters", {}).get("accounts", 0))
        self._next_account_id = max(max_account_id, counter_account_id) + 1


    def save_to_json(self) -> dict:
        """
        Helper method to turn attributes into a dict for json, which can then be stored in a file.
        
        Returns: 
            dict: Dictionary that holds lists of each data type stored.
        """
        users = []
        for user in self.users:
            users.append(
                {
                    "id": user.get_id(),
                    "username": user.get_name(),
                    "hashed_password": user.get_passwd(),
                    "permission": self._user_permission(user),
                    "bank_account_ids": [account.account_id for account in user.get_accounts()],
                }
            )

        accounts = []
        transaction = []
        for account in self.accounts:
            accounts.append(
                {
                    "id": account.account_id,
                    "balance": account.balance,
                    "frozen": account.is_frozen,
                    "type": "savings" if isinstance(account, SavingsAccount) else "checking",
                    "transactions": []
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
        """
        Creates login token to match new connection with a user.

        Args:
            user_id (int): ID of the user that is requesting a connection.
            permission (int): Permission level of the user account trying to connect.

        Returns:
            str: Login token for the new connection.
        """
        minutes_valid = int(os.getenv("TOKEN_LIFETIME_MINUTES", "60"))
        expire = datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)
        payload = {"user_id": user_id, "permission": permission, "exp": expire}
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)


    def register_user(self, username: str, password: str) -> bool:
        """
        Creates a new user account, and adds it to the user list.

        Args:
            username (str): Name of the user account to be created.
            password (str): Password for the user account to be created.

        Returns:
            bool: True if the user was created successfully, false if the username already exists.
        """
        if self.get_user_by_name(username) is not None:
            return False

        user = Customer(
            username,
            id=self._next_user_id,
            passwd=self._password_hasher.hash(password),
            bank=self,
            permissions=0,
        )
        self._next_user_id += 1
        self.add_user(user)
        return True


    def login_user(self, username: str, password: str) -> bool | str:
        """
        Attempts a user login, checks to see if password matches, returns login token for the connection.

        Args:
            username (str): Username of the user account that is attempting to log in.
            password (str): Given password of the user account that is attempting a log in.

        Returns: 
            bool: If user login fails, returns false.
            str: If user login works, returns user login token.
        """
        user = self.get_user_by_name(username)
        if user is None:
            return False

        try:
            self._password_hasher.verify(user.get_passwd(), password)
        except (VerifyMismatchError, ValueError, TypeError):
            return False

        return self.generate_login_token(user.get_id(), self._user_permission(user))


    def ensure_root_user(self) -> bool:
        """
        Creates a root user if it doesn't already exist, ensuring that one admin user exists on each new bank.

        Returns:
            bool: True if root user gets created, false if root user already exists.
        """
        if self.get_user_by_name("root") is not None:
            return False

        user = Customer(
            "root",
            self._next_user_id,
            self._password_hasher.hash(os.getenv("ROOT_PASSWORD", "root")),
            permissions=2,
        )
        self._next_user_id += 1
        self.add_user(user)
        return True


    def _user_permission(self, user: Customer) -> int:
        """
        Checks user's permissions, returning their permission value.

        Args:
            user (Customer): User to check permissions of.
        
        Returns: 
            int: Permissions level of the user.
        """
        return int(getattr(user, "permissions", 0))


    def get_total_balance(self, user: Customer | None = None) -> float:
        """
        returns the total balance of all of a user's bank accounts, or the
        entire bank if no user is given

        Args:
        user (Customer): optional -- the user to sum account balances for
        """
        if user is None:
            return sum(account.balance for account in self.accounts)
        return sum(account.balance for account in user.get_accounts().values())


    def _compound_savings_interest(self) -> None:
        """compounds the interest of all accounts in the bank"""
        for account in self.get_all_accounts(only_savings=True):
            account.compound_interest()


    def _reset_withdraw_limits(self) -> None:
        """resets the withdraw limits of all bank accounts in the bank"""
        for account in self.get_all_accounts(only_savings=True):
            account.reset_withdraw_limit()


    def daily_changes(self) -> None:
        """performs the daily changes for compound interest and resetting withdraw limits"""
        self._compound_savings_interest()
        self._reset_withdraw_limits()


    def add_user(self, user: Customer) -> None:
        """
        adds a given customer to the bank

        Args:
        user (Customer): the user to add
        """
        if self.get_user_by_id(user.get_id()) is not None:
            raise KeyError(f"User id already exists: {user.get_id()}")
        self.users[user.get_id] = user
        self._next_user_id = max(self._next_user_id, user.get_id() + 1)


    def add_account(self, account: CheckingAccount) -> None:
        """
        adds a given bank account to the bank

        Args:
        account (CheckingAccount): the bank account to add
        """
        if any(existing.account_id == account.account_id for existing in self.accounts):
            raise KeyError(f"Account id already exists: {account.account_id}")
        self.accounts[account.get_account_id] = account
        self._next_account_id = max(self._next_account_id, account.account_id + 1)

    def _next_account_num(self) -> int:
        """returns and increments the global account_num value for id purposes"""
        next_id = self._next_account_id
        self._next_account_id += 1
        return next_id


    def create_account_for_user(self, user: Customer, account_type: str = "checking") -> CheckingAccount:
        """
        creates a bank account for a given user and adds it to the bank

        Args:
        user (Customer): the customer to add the new accoun to
        account_type (str): the type of account, either checking or savings
        """
        if account_type == "savings":
            account = SavingsAccount(self._next_account_num(), self, balance)
        else:
            account = CheckingAccount(self._next_account_num(), self, balance)

        self.add_account(account)
        user.register_account(account)
        return account

    
    def get_accounts_for_user(self, user: Customer) -> dict[int, CheckingAccount]:
        """
        returns all bank accounts of a given user
        
        Args:
        user (Customer): the customer to find all accounts of
        """
        return user.get_accounts()


    def get_account_by_id(self, account_id: int) -> CheckingAccount | None:
        """
        returns a bank account by id search, none if not found

        Args:
        account_id (int): the id of the account to search for
        """
        for account in self.accounts:
            if account.account_id == account_id:
                return account
        return None
    

    def get_all_users(self) -> dict[int, Customer]:
        """
        returns the dict of all users in the bank
        """
        return self.users


    def get_all_accounts(self, only_savings: bool = False) -> dict[int, CheckingAccount]:
        """
        returns a dict of all accounts (or all savings accounts)

        Args:
        only_savings (bool): if True, only savings accounts will be returned
        """
        if only_savings:
            savings = {}
            for acc in self.accounts:
                if isinstance(self.accounts[acc], SavingsAccount):
                    savings[acc] = self.accounts[acc]
            return savings
        else:
            return self.accounts


    def get_user_by_id(self, user_id: int) -> Customer | None:
        """
        returns a given user found by id, none if not found

        Args:
        id (int): the id to search for
        """
        for key,user in self.users.items():
            if user.get_id() == user_id:
                return user
        return None
    
    def get_user_by_name(self, username: str) -> Customer | None:
        """
        returns a given user found by name, none if not found

        Args:
        username (str): the username to search for
        """
        for user in self.users.values():
            if user.get_name() == username:
                return user
        return None
    
    def get_next_transaction_id(self) -> int:
        """Returns a num for the next absolute transaction ID, increments the next ID by 1"""
        temp = self._next_transaction_id
        self._next_transaction_id += 1
        return temp


    def get_account(self, account_id: int) -> CheckingAccount:
        """
        returns a specific account based on account id

        Args:
        account_id (int): the id of the account to return
        """
        return self.accounts[account_id]


    def remove_user(self, identifier) -> Customer:
        """
        removes a user account based on either id or name

        Args:
        identifier (str or int): the key used to remove the account, either id or name
        """
        if isinstance(identifier, str):
            self.remove_user_by_name(identifier)
        else:
            self.remove_user_by_id(identifier)

    def remove_user_by_id(self, user_id: int) -> Customer:
        """
        removes a user account from the bank via id

        Args:
        id (int): the id of the user to be removed
        """
        for key,cust in self.users.items():
            if cust.get_id() == user_id:
                del self.users[key]
                break


    def remove_user_by_name(self, username: str) -> Customer:
        """
        removes a user account from the bank via username

        Args:
        username (str): the name of the user to be removed
        """
        for key,value in self.users.items():
            if value.get_name() == username:
                del self.users[key]
                break


    def remove_account(self, id: int) -> CheckingAccount:
        """
        removes a bank account from the bank via account_id

        Args:
        id (int): the account_id of the account to be removed
        """
        for key,acc in self.accounts.items():
            if acc.get_account_id() == id:
                del self.accounts[key]
                break

