import sys
sys.path.append('./server/src')

from transaction import Transaction
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bank import Bank
from exceptions.amount_invalid_exception import AmountInvalidException
from exceptions.insufficient_funds_exception import InsufficientFundsException
from exceptions.account_frozen_exception import AccountFrozenException

from decimal import Decimal

class CheckingAccount:
    """
    A class used to represent a checking account.

    Attributes:
        account_id (int): The account number of the checking account.
        balance (float): The current balance of the checking account.
        frozen (bool): Whether the account is frozen or not.
        transactions (dict[int, Transaction]): The list of transactions associated with this account, key is relative ID.
        next_transaction_num (int): Next relative ID of transaction.
    """


    def __init__(self, account_id: int, bank: "Bank", balance: float = 0.0) -> None:
        """
        Initialize the CheckingAccount with the params account number and optional balance.
        Also initalizes the attributes is_frozen to false and transactions to an empty list of transactions.

        Args:
            account_id (int): The account number of the checking account.
            bank (Bank): The bank the account belongs to.
            balance (float, optional): The initial balance of the checking account.
                Defaults to 0.0.

        Raises:
            AmountInvalidException: If the inputted balance is invalid.
        """

        if balance != 0.0 and not self._is_amount_valid(balance):
            raise AmountInvalidException(balance)

        self.account_id: int = account_id
        self.balance: float = balance
        self.frozen: bool = False
        self.transactions: dict[int, Transaction] = {}
        self.next_transaction_id = 0
        self.bank = bank

        if balance != 0.0:
            self.transactions[self.next_transaction_id] = Transaction(self.bank.get_next_transaction_id(), self.next_transaction_id, self.account_id, balance)
            self.next_transaction_id += 1

 
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
        if self.frozen:
            raise AccountFrozenException(self.account_id)
        elif not self._is_amount_valid(amount):
            raise AmountInvalidException(amount)
        elif amount > self.balance:
            raise InsufficientFundsException(amount, self.balance)
        
        self.balance -= amount
        self.transactions[self.next_transaction_id] = Transaction(self.bank.get_next_transaction_id(), self.next_transaction_id, self.account_id, (amount * -1))
        self.next_transaction_id += 1


    def deposit(self, amount: float) -> None:
        """
        Deposits a specified amount into the checking account.

        Args:
            amount (float): The amount to deposit into the account.

        Raises:
            AmountInvalidException: If the deposit amount is non-positive or > 2 decimal places.
            AccountFrozenException: If the account is frozen.
        """
        if self.frozen:
            raise AccountFrozenException(self.account_id)
        elif not self._is_amount_valid(amount):
            raise AmountInvalidException(amount)
        
        self.balance += amount
        self.transactions[self.next_transaction_id] = Transaction(self.bank.get_next_transaction_id(), self.next_transaction_id, self.account_id, amount)
        self.next_transaction_id += 1


    def transfer(self, amount: float, rec_account: 'CheckingAccount') -> None:
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
        self.withdraw(amount)    
        rec_account.deposit(amount) 


    def is_frozen(self) -> bool:
        """
        Checks if the account is currently frozen.

        Returns:
            bool: True if the account is frozen, False otherwise.
        """
        return self.frozen


    def toggle_frozen(self) -> bool:
        """
        Toggles the frozen status of the account.

        Returns:
            bool: The new frozen status of the account.
        """
        self.frozen = not self.frozen
        return self.frozen


    def check_balance(self) -> float:
        """
        Returns the current balance of the account.

        Returns:
            float: The current balance of the account.
        """
        return self.balance

    
    def get_balance(self) -> float:
        """
        Returns the current balance of the account.

        Returns:
            float: The current balance of the account.
        """
        return self.balance


    def get_account_id(self) -> int:
        """
        Returns the account id.

        Returns:
            int: The account ID of the account.
        """
        return self.account_id


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
        if (transaction_num < 0):
            raise IndexError("Transaction number must be non-negative.")
        
        # If is_relative = false, search by absolute id. If is_relative = true, search by relative id.
        if (is_relative):
            for transaction in self.transactions.values():
                if (transaction.get_relative_id() == transaction_num):
                    return transaction
        else:
            for transaction in self.transactions.values():
                if (transaction.get_absolute_id() == transaction_num):
                    return transaction
                
        raise KeyError(f"Transaction with number {transaction_num} not found in list of transactions for {self.account_id}.")


    def get_all_transactions(self) -> dict[int, Transaction]:
        """
        Returns a list of all transactions associated with the account.

        Returns:
            list[Transaction]: A list of all transactions on the account.
        """
        return self.transactions


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
        if (transaction_num < 0):
            raise IndexError("Transaction number must be non-negative.")
        
        # If is_relative = false, search by absolute id. If is_relative = true, search by relative id.
        if (is_relative):
            for transaction in self.transactions.values():
                if (transaction.get_relative_id() == transaction_num):
                    return str(transaction)
        else:
            for transaction in self.transactions.values():
                if (transaction.get_absolute_id() == transaction_num):
                    return str(transaction)
                
        raise KeyError(f"Transaction with number {transaction_num} not found in list of transactions for {self.account_id}.")

    def get_all_transaction_str(self) -> str:
        """
        Retrieves all transactions as one human-readable string.

        Returns:
            str: The human-readable string showing information about all transactions, with a new line between each one.
        """
        return '\n'.join(str(transaction) for transaction in self.transactions.values())


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

    def get_account_type(self) -> str:
        """
        Returns the type of the account as a string.

        Returns:
            str: The type of the account.
        """
        return "checking"