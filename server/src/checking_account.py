from transaction import Transaction

class Checking_Account:
    """
    A class used to represent a checking account.

    Attributes:
        account_num (int): The account number of the checking account.
        balance (float): The current balance of the checking account.
        is_frozen (bool): Whether the account is frozen or not.
        transactions (list[Transaction]): The list of transactions associated with this account.
    """

    def __init__(self, account_num: int, balance: float = 0.0) -> None:
        """
        Initialize the Checking_Account with the params account number and optional balance.
        Also initalizes the attributes is_frozen to false and transactions to an empty list of transactions.

        Args:
            account_num (int): The account number of the checking account.
            balance (float, optional): The initial balance of the checking account.
                Defaults to 0.0.
        """
        pass
    
    def withdraw(self, amount: float) -> None:
        """
        Withdraws a specified amount from the checking account.

        Args:
            amount (float): The amount to withdraw from the account.

        Raises:
            InsufficientFundsException: If the withdraw amount exceeds the balance.
        """
        pass

    def deposit(self, amount: float) -> None:
        """
        Deposits a specified amount into the checking account.

        Args:
            amount (float): The amount to deposit into the account.
        """
        pass

    def transfer(self, amount: float, rec_account: 'Checking_Account') -> None:
        """
        Transfers a specified amount from this account to a receiving account.

        Args:
            amount (float): The amount to transfer.
            rec_account (Checking_Account): The account receiving the transfer.

        Raises:
            InsufficientFundsException: If the withdraw amount exceeds the balance.
        """
        pass

    def is_frozen(self) -> bool:
        """
        Checks if the account is currently frozen.

        Returns:
            bool: True if the account is frozen, False otherwise.
        """
        pass

    def toggle_frozen(self) -> bool:
        """
        Toggles the frozen status of the account.

        Returns:
            bool: The new frozen status of the account.
        """
        pass

    def check_balance(self) -> float:
        """
        Returns the current balance of the account.

        Returns:
            float: The current balance of the account.
        """
        pass

    def get_acct_num(self) -> int:
        """
        Returns the account number.

        Returns:
            int: The account number of the account.
        """
        pass

    def get_transaction(self, transaction_num: int) -> Transaction:
        """
        Retrieves a specific transaction by its number.

        Args:
            transaction_num (int): The transaction number to retrieve.

        Raises:
            KeyError: Transaction number not found in list of transactions.

        Returns:
            Transaction: The transaction object corresponding to the transaction number.
        """
        pass

    def get_all_transactions(self) -> list[Transaction]:
        """
        Returns a list of all transactions associated with the account.

        Returns:
            list[Transaction]: A list of all transactions on the account.
        """
        pass
