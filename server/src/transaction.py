import sys
sys.path.append('./server/src')

from datetime import datetime, timezone
from transaction_type import TransactionType

class Transaction:
    """
    A class used to represent a single transaction.

    Attributes: 
        absolute_transaction_id (int): ID of the transaction relative to the total bank transactions.
        relative_transaction_id (int): ID of the transaction relative to the account.
        account_id (int): Account number where the transaction occured.
        timestamp (datetime): When the transaction occured in UTC.
        amount (float): The change in account balance of the transaction.
        balance (float): The balance of the account post-transaction.
        type (TransactionType): The type of transaction.
        description (str): The description of the transaction.
    """
    def __init__(self, absolute_transaction_id: int, relative_transaction_id: int, account_id: int, amount: float, balance: float, type: TransactionType, transfer_account_id: int | None = None, datetime_str: str | None = None) -> None:
        """
        Initialize the Transaction with the transaction ids, account number, timestamp, balance, amount, type, description and potential transfer_account_id.
        
        Args:
            absolute_transaction_id (int): Absolute ID of the transaction.
            relative_transaction_id (int): Relative ID of the transaction.
            account_id (int): Account number where the transaction occurred.
            amount (float): The change in account balance of the transaction.
            balance (float): The balance of the account post-transaction.
            type (TransactionType): Type of the transaction.
            transfer_account_id (int, optional): Account number the transfer is occuring with (if type is transfer).
            datetime_str (str, optional): Passes in datetime of transaction for loading from database (optional).
        """
        self.absolute_transaction_id: int = absolute_transaction_id
        self.relative_transaction_id: int = relative_transaction_id
        self.account_id: int = account_id
        self.amount: float = amount
        self.balance: float = balance
        self.type: TransactionType = type
        self.transfer_account_id: int | None = transfer_account_id

        if datetime_str is None:
            self.timestamp: datetime = datetime.now(timezone.utc)

        match type.value:
            case 1:
                self.description = f"Withdrawal of ${abs(self.amount):.2f}"
            case 2:
                self.description = f"Deposit of ${abs(self.amount):.2f}"
            case 3:
                self.description = f"Transfer to ACC-{self.transfer_account_id} of ${abs(self.amount):.2f}"
            case 4:
                self.description = f"Transfer from ACC-{self.transfer_account_id} of ${abs(self.amount):.2f}"
            case 5:
                self.description = f"New account created with balance ${abs(self.amount):.2f}"
            case 6:
                self.description = f"Collected interest amount of ${abs(self.amount):.2f}"

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
        return self.balance

    def get_account_id(self) -> int:
        """
        Returns the account number that the transaction belongs to.

        Returns:
            int: The amount number that the transaction belongs to.
        """
        return self.account_id
    
    def get_type(self) -> TransactionType:
        """
        Returns the type of transaction this transaction is.

        Returns:
            TransactionType: The type of transaction this transaction is.
        """
        return self.type

    def get_description(self) -> str:
        """
        Returns a brief description of the transaction.
    
        Returns:
            str: Brief description of the transaction.
        """
        return self.description
    
    def get_transfer_account_id(self) -> int | None:
        """
        Returns the transfer account ID of the transaction.
    
        Returns:
            int | None: Transfer account ID of the transaction.
        """
        return self.transfer_account_id
