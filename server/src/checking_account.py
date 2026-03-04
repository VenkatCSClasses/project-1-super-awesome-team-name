from server.src.transaction import Transaction
from server.src.exceptions.amount_invalid_exception import AmountInvalidException
from server.src.exceptions.insufficient_funds_exception import InsufficientFundsException

from decimal import Decimal

class CheckingAccount:
    """
    A class used to represent a checking account.

    Attributes:
        account_num (int): The account number of the checking account.
        balance (float): The current balance of the checking account.
        is_frozen (bool): Whether the account is frozen or not.
        transactions (list[Transaction]): The list of transactions associated with this account.
    """

    def __init__(self, account_num: int, balance: float = 0.0) -> None:
        """
        Initialize the CheckingAccount with the params account number and optional balance.
        Also initalizes the attributes is_frozen to false and transactions to an empty list of transactions.

        Args:
            account_num (int): The account number of the checking account.
            balance (float, optional): The initial balance of the checking account.
                Defaults to 0.0.

        Raises:
            AmountInvalidException: If the inputted balance is invalid.
        """

        if not self._is_amount_valid(balance):
            raise AmountInvalidException(balance)
        
        self.account_num: int = account_num
        self.balance: float = balance
        self.is_frozen: bool = False
        self.transactions: list[Transaction] = []
    
    def withdraw(self, amount: float) -> None:
        """
        Withdraws a specified amount from the checking account.

        Args:
            amount (float): The amount to withdraw from the account.

        Raises:
            AmountInvalidException: If the withdraw amount is non-positive or > 2 decimal places.
            InsufficientFundsException: If the withdraw amount exceeds the balance.
            AccountFrozenException: If the account is frozen.
        """
        pass

    def deposit(self, amount: float) -> None:
        """
        Deposits a specified amount into the checking account.

        Args:
            amount (float): The amount to deposit into the account.

        Raises:
            AmountInvalidException: If the deposit amount is non-positive or > 2 decimal places.
            AccountFrozenException: If the account is frozen.
        """
        pass

    def transfer(self, amount: float, rec_account: CheckingAccount) -> None:
        """
        Transfers a specified amount from this account to a receiving account.

        Args:
            amount (float): The amount to transfer.
            rec_account (Checking_Account): The account receiving the transfer.

        Raises:
            AmountInvalidException: If the transfer amount is non-positive or > 2 decimal places.
            InsufficientFundsException: If the withdraw amount exceeds the balance.
            AccountFrozenException: If the account is frozen.
        """
        pass

    def is_frozen(self) -> bool:
        """
        Checks if the account is currently frozen.

        Returns:
            bool: True if the account is frozen, False otherwise.
        """
        pass

    def toggle_frozen(self) -> bool:
        """
        Toggles the frozen status of the account.

        Returns:
            bool: The new frozen status of the account.
        """
        pass

    def check_balance(self) -> float:
        """
        Returns the current balance of the account.

        Returns:
            float: The current balance of the account.
        """
        return self.balance

    def get_acct_num(self) -> int:
        """
        Returns the account number.

        Returns:
            int: The account number of the account.
        """
        pass

    def get_transaction(self, transaction_num: int, is_relative: bool = False) -> Transaction:
        """
        Retrieves a specific transaction by its number.

        Args:
            transaction_num (int): The transaction number to retrieve.
            is_relative (bool, optional): Whether or not the transaction ID is relative (account) or absolute (bank).
                Defaults to False.

        Raises:
            IndexError: If transaction_num is negative.
            KeyError: Transaction number not found in list of transactions.

        Returns:
            Transaction: The transaction object corresponding to the transaction number.
        """
        pass

    def get_all_transactions(self) -> list[Transaction]:
        """
        Returns a list of all transactions associated with the account.

        Returns:
            list[Transaction]: A list of all transactions on the account.
        """
        pass

    def get_transaction_str(self, transaction_num: int, is_relative: bool = False) -> str:
        """
        Retrieves a specific transaction by its number as a human-readable string.

        Args:
            transaction_num (int): The transaction number to retrieve.
            is_relative (bool, optional): Whether or not the transaction ID is relative (account) or absolute (bank).
                Defaults to False.

        Raises:
            IndexError: If transaction_num is negative.
            KeyError: Transaction number not found in list of transactions.

        Returns:
            str: The human-readable string showing information about the transaction.
        """
        pass

    def get_all_transaction_str(self) -> str:
        """
        Retrieves all transactions as one human-readable string.

        Returns:
            str: The human-readable string showing information about all transactions.
        """
        pass

    @staticmethod
    def _is_amount_valid(amount: float) -> bool:
        """
        Returns true if an amount is valid (non-negative and 2 or less decimal places), false if not.
        Protected security to be used by subclass SavingsAccount.

        Returns:
            bool: True if valid, false if invalid.
        """

        if amount <= 0:
            return False
        
        # Using Decimal and isInteger to do integer rounding in python to determine 2+ decimal place
        dec = Decimal(str(amount)) * 100

        return dec == dec.to_integral()
