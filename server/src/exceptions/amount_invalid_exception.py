class AmountInvalidException(Exception):
    """
    Exception raised when a dollar amount is either non-positive or more than two decimal places.
    """

    def __init__(self, amount: float):
        """
        Initialize the AmountInvalidException

        Args:
            amount (float): The amount that is invalid.
        """
        self.amount = amount

        if amount <= 0:
            super().__init__(f"Cannot do this operation with the non-positive amount of {self.amount}.")
        else:
            super().__init__(f"Cannot do this operation with the amount {self.amount} as it has more than two decimal places.")
            


   