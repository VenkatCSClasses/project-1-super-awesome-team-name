import sys
sys.path.append('./server/src')

from customer import Customer
from checking_account import CheckingAccount
from transaction import Transaction
from savings_account import SavingsAccount

class Bank:
    """
    A class used to represent a bank.

    Attributes:
        users (list[User]): The users associated with the bank.
        accounts (list[CheckingAccount]): The accounts associated with the bank.
    """
    
    def __init__(self, json_data: dict = None) -> None:
        """Initialize the Bank with empty lists for users and accounts."""
        if json_data is not None:
            for user_record in json_data.get("users", []):
                new_user = Customer() 
                for account_id in user_record.get("bank_account_ids", []):
                    new_user.register_account(CheckingAccount(account_id))
                self.add_user(new_user)

            for account_record in json_data.get("accounts", []):
                if account_record["type"] == "checking":
                    account = CheckingAccount(account_record["id"], account_record["balance"])
                else:
                    account = SavingsAccount(account_record["id"], account_record["balance"])

                account.is_frozen = account_record["frozen"]
                for transaction_record in account_record.get("transactions", []):
                    account.transactions.append(
                        Transaction(
                            transaction_record["id"],
                            transaction_record["type"],
                            transaction_record["amount"],
                            transaction_record["timestamp"],
                            transaction_record.get("source_account_id", None),
                            transaction_record.get("destination_account_id", None)
                        )
                    )
    
    def get_total_balance(self) -> float:
        """
        Calculate the sum of balances across all bank accounts.

        Returns:
            float: Total sum of balances across all accounts.
        """
        pass

    def _compound_savings_interest(self) -> None:
        """Compounds interest across all savings accounts in the bank."""
        pass

    def _reset_withdraw_limits(self) -> None:
        """Resets withdraw limits across all savings accounts in the bank."""

    def daily_changes(self) -> None:
        """Runs the compound savings interest and resets withdraw limits."""

    def add_user(self, user: Customer) -> None:
        """
        Adds a new user to the bank.

        Args:
            user (User): The User that is being added to the bank.
        """
        pass
    
    def add_account(self, account: CheckingAccount) -> None:
        """
        Adds a new account to the bank.

        Args:
            account (CheckingAccount): The account object that is being added to the bank.
        """
        pass

    def get_all_users(self) -> list[Customer]:
        """
        Returns all the users that belong to the bank.

        Returns:
            list[User]: A list of all the users that belong to the bank.
        """
        pass
    
    def get_all_accounts(self, only_savings: bool = False) -> list[CheckingAccount]:
        """
        Returns a list of accounts that belong to the bank.

        Args:
            only_savings (bool, optional): Whether or not to just return savings accounts.
                Defaults to False.
        
        Returns:
            list[CheckingAccount]: A list of accounts that belong to the bank.
        """
        pass

    def get_user(self, user_id: int) -> Customer:
        """
        Returns a specific user that belongs to the bank.

        Args:
            user_id: The ID of the user that is being returned.
        
        Raises:
            KeyError: ID not found in the list of users.

        Returns:
            User: User that is being returned.
        """
        pass

    def get_account(self, account_num: int) -> CheckingAccount:
        """
        Returns a specific account that belongs to the bank.

        Args:
            account_id: The number of the account that is being returned.
        
        Raises:
            KeyError: Account number not found in the list of accounts.

        Returns:
            CheckingAccount: Account that is being returned.
        """
        pass
    
    def remove_user(self, id: int) -> Customer:
        """
        Removes a user from the bank.

        Args:
            id (int): ID of the user to remove.
        
        Raises:
            KeyError: ID not found in the list of users.

        Returns:
            User: The user removed from the bank.
        """
        pass

    def remove_account(self, id: int) -> CheckingAccount:
        """
        Removes an account from the bank.

        Args:
            id (int): ID of the account to remove.
        
        Raises:
            KeyError: ID not found in the list of accounts.

        Returns:
            CheckingAccount: The account removed from the bank.
        """
        pass
    

    





    
