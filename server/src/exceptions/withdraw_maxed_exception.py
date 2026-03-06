class WithdrawMaxedException(Exception):
    """
    Exception raised when the withdrawal limit has been reached for savings accounts.
    """

    def __init__(self, max_withdraw_limit: float, curr_withdraw_limit: float, withdraw_amount: float):
        """
        Initialize the WithdrawMaxedException.

        Args:
            max_withdraw_limit (float): The maximum withdrawal limit.
            curr_withdraw_limit (float): The current withdrawal limit.
            withdraw_amount (float): The amount attempted to be withdrawn.
        """
        self.max_withdraw_limit = max_withdraw_limit
        self.curr_withdraw_limit = curr_withdraw_limit
        self.withdraw_amount = withdraw_amount

        super().__init__(f"Attempted withdraw amount of {self.withdraw_amount}, along with the current daily withdraw limit of {self.curr_withdraw_limit} exceeds the max withdraw limit of {self.max_withdraw_limit}.")