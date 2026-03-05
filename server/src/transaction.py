from datetime import datetime

class Transaction:
    """
    A class used to represent a single transaction.

    Attributes: 
        relative_transaction_id (int): ID of the transaction relative to the account.
        absolute_transaction_id (int): ID of the transaction relative to the total bank transactions.
        account_num (int): Account number where the transaction occured.
        timestamp (datetime): When the transaction occured in UTC.
        amount (float): The change in account balance of the transaction.
    """
    def __init__(self, absolute_transaction_id: int, relative_transaction_id: int, account_num: int, amount: float) -> None:
        """
        Initialize the Transaction with the transaction ids, account number, timestamp, and amount.
        
        Args:
            absolute_transaction_id (int): Absolute ID of the transaction.
            relative_transaction_id (int): Relative ID of the transaction.
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

    def get_account_num(self) -> int:
        """
        Returns the account number that the transaction belongs to.

        Returns:
            int: The amount number that the transaction belongs to.
        """
        pass

    def __str__(self) -> str:
        """
        toString method to turn the transaction into a human-readable string.
        Format: Transaction (Absolute ID: {abs_id}, Relative ID: {rel_id}) of account {acc_num} 
                occured on {timestamp} with the amount changed of {amount}.
                Timestamp format is ("%A, %B %d, %Y, %H:%M")
        
        Returns:
            str: Human-readable string showing information about the transaction.
        """
        pass
