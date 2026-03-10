from datetime import datetime, timezone

class Transaction:
    """
    A class used to represent a single transaction.

    Attributes: 
        absolute_transaction_id (int): ID of the transaction relative to the total bank transactions.
        relative_transaction_id (int): ID of the transaction relative to the account.
        account_num (int): Account number where the transaction occured.
        timestamp (datetime): When the transaction occured in UTC.
        amount (float): The change in account balance of the transaction.
        balance (float): The balance of the account post-transaction.
    """
    def __init__(self, absolute_transaction_id: int, relative_transaction_id: int, account_id: int, amount: float, balance: float) -> None:
        """
        Initialize the Transaction with the transaction ids, account number, timestamp, and amount.
        
        Args:
            absolute_transaction_id (int): Absolute ID of the transaction.
            relative_transaction_id (int): Relative ID of the transaction.
            account_num (int): Account number where the transaction occurred.
            amount (float): The change in account balance of the transaction.
            balance (float): The balance of the account post-transaction.
        """
        self.absolute_transaction_id: int = absolute_transaction_id
        self.relative_transaction_id: int = relative_transaction_id
        self.account_id: int = account_id
        self.amount: float = amount

        self.timestamp: datetime = datetime.now(timezone.utc)

    def get_absolute_id(self) -> int:
        """
        Returns the relative ID of the transaction based on the account.

        Returns:
            int: The relative ID of the transaction.
        """
        return self.absolute_transaction_id

    def get_relative_id(self) -> int:
        """
        Returns the absolute ID of the transaction based on the entire bank.

        Returns:
            int: The absolute ID of the transaction.
        """
        return self.relative_transaction_id
    
    def get_time(self) -> datetime:
        """
        Returns when the transaction occurred.

        Returns:
            datetime: The timestamp of when the transaction occurred.
        """
        return self.timestamp

    def get_amount(self) -> float:
        """
        Returns the amount changed of the transaction.

        Returns:
            float: The amount changed of the transaction.
        """
        return self.amount
    
    def get_post_balance(self) -> float:
        """
        Returns the balance of the account after the transaction.

        Returns:
            float: The balance of the account after the transaction.
        """

    def get_account_id(self) -> int:
        """
        Returns the account number that the transaction belongs to.

        Returns:
            int: The amount number that the transaction belongs to.
        """
        return self.account_id

    def __str__(self) -> str:
        """
        toString method to turn the transaction into a human-readable string.
        Format: Transaction (Absolute ID: {abs_id}, Relative ID: {rel_id}) of account {acc_num} 
                occured on {timestamp} of {amount}, with the new balance being {balance}.
                Timestamp format is ("%A, %B %d, %Y, %H:%M")
        
        Returns:
            str: Human-readable string showing information about the transaction.
        """
        time_readable: str = self.timestamp.strftime("%A, %B %d, %Y, %H:%M")

        return f"Transaction (Absolute ID: {self.absolute_transaction_id}, Relative ID: {self.relative_transaction_id}) of account {self.account_id} occured on {time_readable} with the amount changed being {self.amount}."
