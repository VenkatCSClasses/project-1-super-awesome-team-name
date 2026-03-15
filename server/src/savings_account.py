import sys
sys.path.append("./server/src")

from checking_account import CheckingAccount
from transaction import Transaction
from transaction_type import TransactionType
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bank import Bank

from exceptions.withdraw_maxed_exception import WithdrawMaxedException

import os
from dotenv import load_dotenv
load_dotenv()

class SavingsAccount(CheckingAccount):
    """
    A class used to represent a savings account.

    Attributes:
        account_num (int): The account number of the savings account.
        balance (float): The current balance of the savings account.
        is_frozen (bool): Whether the account is frozen or not.
        transactions (list[Transaction]): The list of transactions associated with this account.
        curr_withdraw_limit (float): Current remaining withdraw limit on the day.
    """

    def __init__(self, account_id: int, bank: Bank, balance: float = 0.0, transaction_needed: bool = True, next_transaction_id: int = 1) -> None:
        """
        Initialize the SavingsAccount with the account number and optional balance.
        Also initalizes the is_frozen to false, transactions to an empty list, curr_withdraw_total to 0.0.
        max_withdraw_total and daily_interest are env variable, but default is 10,000 and 0.05%.

        Args:
            account_num (int): The account number of the savings account.
            balance (float, optional): The initial balance of the savings account.
                Defaults to 0.0.
        """
        super().__init__(account_id, bank, balance, transaction_needed, next_transaction_id)
        self.curr_withdraw_limit = float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))


    def withdraw(self, amount: float, is_transfer: bool = False, transfer_account_id: int | None = None) -> None:
        """
        Withdraws a specified amount from the checking account.
        Ensures withdrawal doesn't exceed current withdraw total

        Args:
            amount (float): The amount to withdraw from the account.
            is_transfer (bool): If the withdrawal is from a transfer.
            transfer_account_id (int): Account the deposit is transferring to.

        Raises:
            AmountInvalidException: If the withdraw amount is non-positive or > 2 decimal places.
            InsufficientFundsException: If withdraw amount exceeds balance.
            WithdrawMaxedException: If withdraw amount exceeds withdraw limit (inclusive).
            AccountFrozenException: If the account is frozen.
        """
        if (self.curr_withdraw_limit - amount < 0):
            raise WithdrawMaxedException(float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)), self.curr_withdraw_limit, amount)

        super().withdraw(amount, is_transfer, transfer_account_id)

        self.curr_withdraw_limit -= amount


    def transfer(self, rec_account: CheckingAccount, amount: float) -> None:
        """
        Transfers a specified amount from this account to a receiving account.

        Args:
            rec_account (CheckingAccount): The account receiving the transfer.
            amount (float): The amount to transfer.

        Raises:
            AmountInvalidException: If the withdraw amount is non-positive or > 2 decimal places.
            InsufficientFundsException: If the withdraw amount exceeds the balance.
            WithdrawMaxedException: If withdraw amount exceeds withdraw limit (inclusive).
            AccountFrozenException: If the account is frozen.
        """
        if (self.curr_withdraw_limit - amount < 0):
                        raise WithdrawMaxedException(float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)), self.curr_withdraw_limit, amount)

        super().transfer(rec_account, amount)


    def get_interest_amount(self) -> float:
        """
        Returns the interest amount.

        Returns:
            float: The interest amount.
        """
        return float(os.getenv("DAILY_INTEREST", 0.0005))

    def get_current_withdraw_limit(self) -> float:
        """
        Returns the current withdraw limit.

        Returns:
            float: The current withdraw limit.
        """
        return self.curr_withdraw_limit
        

    def get_max_withdraw_limit(self) -> float:
        """
        Returns the max withdraw limit.

        Returns:
            float: The max withdraw limit.
        """
        return float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))

    def get_account_type(self) -> str:
        """Returns the account type label used by the API and UI."""
        return "savings"


    def compound_interest(self) -> None:
        """Compounds the interest of the savings account."""
        interest_amount = round(self.balance * (float(os.getenv("DAILY_INTEREST", 0.0005))), 2)

        self.balance += interest_amount

        self.log_transaction(interest_amount, TransactionType.INTEREST)

        

    def reset_withdraw_limit(self) -> None:
        """Resets the current withdraw limit back to full."""
        self.curr_withdraw_limit = float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
        
