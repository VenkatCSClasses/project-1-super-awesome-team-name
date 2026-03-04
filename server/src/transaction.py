from datetime import datetime

class Transaction:
    """
    A class used to represent a single transaction.

    Attributes: 
        timestamp (datetime): When the transaction occured.
        amount (float): The change in account balance of the transaction.
    """
    def __init__(self, amount: float):
        """
        Initialize the Transaction with the amount and timestamp
        
        Args:
            amount (float): The change in account balance of the transaction.
        """
        pass

    def get_time(self) -> datetime:
        """
        Returns when the transaction occurred.

        Returns:
            datetime: The timestamp of when the transaction occurred.
        """
        pass

    def get_amount(self) -> float:
        """
        Returns the amount changed of the transaction.

        Returns:
            float: The amount changed of the transaction.
        """
        pass

    def __str__(self) -> str:
        """
        toString method to turn the transaction into a human-readable string.

        Returns:
            str: Human-readable string showing information about the transaction.
        """
        pass
