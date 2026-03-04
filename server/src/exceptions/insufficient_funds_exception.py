class InsufficientFundsException(Exception):
    """
    Exception raised when there are insufficient funds in an account.
    """

    def __init__(self, withdraw_amount: float, balance: float):
        """
        Initialize the InsufficientFundsException.

        Args:
            withdraw_amount (float): The amount attempted to be withdrawn.
            balance (float): The current balance of the account.
        """
        self.withdraw_amount = withdraw_amount
        self.balance = balance

        super().__init__(f"Attempted withdraw amount of {self.withdraw_amount} exceeds account balance of {self.balance}.")