from datetime import datetime

class Transaction:
    """
    A class used to represent a single transaction.

    Attributes: 
        relative_transaction_id (int): ID of the transaction relative to the account.
        absolute_transaction_id (int): ID of the transaction relative to the total bank transactions.
        account_num (int): Account number where the transaction occured.
        timestamp (datetime): When the transaction occured.
        amount (float): The change in account balance of the transaction.
    """
    def __init__(self, transaction_id: int, account_num: int, amount: float) -> None:
        """
        Initialize the Transaction with the transaction id, account number, timestamp, and amount.
        
        Args:
            relative_transaction_id (int): Relative ID of the transaction.
            absolute_transaction_id (int): Absolute ID of the transaction.
            account_num: Account number where the transaction occurred.
            amount (float): The change in account balance of the transaction.
        """
        pass

    def get_relative_id(self) -> int:
        """
        Returns the relative ID of the transaction based on the account.

        Returns:
            int: The relative ID of the transaction.
        """
        pass

    def get_absolute_id(self) -> int:
        """
        Returns the absolute ID of the transaction based on the entire bank.

        Returns:
            int: The absolute ID of the transaction.
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
