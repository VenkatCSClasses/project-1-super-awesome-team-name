class AccountFrozenException(Exception):
    """
    Exception raised when an account has been frozen but a transaction (not interest transaction) was attempted.
    """

    def __init__(self, account_number: int):
        """
        Initialize the AccountFrozenException.

        Args:
            amount (float): The account number of the account frozen.
        """
        self.account_number = account_number

        super().__init__(f"Cannot perform this transaction on the frozen account with account number of {self.account_number}.")