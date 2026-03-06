from checking_account import CheckingAccount

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
        curr_withdraw_total (float): Current withdraw total on the day.
    """

    def __init__(self, account_num: int, balance: float = 0.0) -> None:
        """
        Initialize the SavingsAccount with the account number and optional balance.
        Also initalizes the is_frozen to false, transactions to an empty list, curr_withdraw_total to 0.0.
        max_withdraw_total and daily_interest are env variable, but default is 10,000 and 0.05%.

        Args:
            account_num (int): The account number of the savings account.
            balance (float, optional): The initial balance of the savings account.
                Defaults to 0.0.
        """
        pass

    def withdraw(self, amount: float) -> None:
        """
        Withdraws a specified amount from the checking account.
        Ensures withdrawal doesn't exceed current withdraw total

        Args:
            amount (float): The amount to withdraw from the account.

        Raises:
            AmountInvalidException: If the withdraw amount is non-positive or > 2 decimal places.
            InsufficientFundsException: If withdraw amount exceeds balance.
            WithdrawMaxedException: If withdraw amount exceeds withdraw limit (inclusive).
            AccountFrozenException: If the account is frozen.
        """

    def transfer(self, amount: float, rec_account: CheckingAccount) -> None:
        """
        Transfers a specified amount from this account to a receiving account.

        Args:
            amount (float): The amount to transfer.
            rec_account (CheckingAccount): The account receiving the transfer.

        Raises:
            AmountInvalidException: If the withdraw amount is non-positive or > 2 decimal places.
            InsufficientFundsException: If the withdraw amount exceeds the balance.
            WithdrawMaxedException: If withdraw amount exceeds withdraw limit (inclusive).
            AccountFrozenException: If the account is frozen.
        """
        pass

    def get_interest_amount(self) -> float:
        """
        Returns the interest amount.

        Returns:
            float: The interest amount.
        """
        pass

    def get_current_withdraw_limit(self) -> float:
        """
        Returns the current withdraw limit.

        Returns:
            float: The current withdraw limit.
        """
        pass

    def get_max_withdraw_limit(self) -> float:
        """
        Returns the max withdraw limit.

        Returns:
            float: The max withdraw limit.
        """
        pass

    def compound_interest(self) -> None:
        """Compounds the interest of the savings account."""
        pass

    def reset_withdraw_limit(self) -> None:
        """Resets the current withdraw limit back to zero each day."""
        pass