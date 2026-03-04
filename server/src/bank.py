from user import User
from checking_account import Checking_Account

class Bank:
    """
    A class used to represent a bank.

    Attributes:
        users (list[User]): The users associated with the bank.
        accounts (list[Checking_Account]): The accounts associated with the bank.
    """
    
    def __init__(self) -> None:
        """Initialize the Bank with empty lists for users and accounts."""
        pass
    
    def get_total_balance(self) -> float:
        """
        Calculate the sum of balances across all bank accounts.

        Returns:
            float: Total sum of balances across all accounts.
        """
        pass

    def compound_savings_interest(self) -> None:
        """Compounds interest across all savings accounts in the bank."""
        pass

    def add_user(self, user: User) -> None:
        """
        Adds a new user to the bank.

        Args:
            user (User): The User that is being added to the bank.
        """
        pass
    
    def add_account(self, account: Checking_Account) -> None:
        """
        Adds a new account to the bank.

        Args:
            account (Checking_Account): The account object that is being added to the bank.
        """
        pass

    def get_all_users(self) -> list[User]:
        """
        Returns all the users that belong to the bank.

        Returns:
            list[User]: A list of all the users that belong to the bank.
        """
        pass
    
    def get_all_accounts(self, only_savings=False) -> list[Checking_Account]:
        """
        Returns a list of accounts that belong to the bank.

        Args:
            only_savings (bool, optional): Whether or not to just return savings accounts.
                Defaults to False.
        
        Returns:
            list[Checking_Account]: A list of accounts that belong to the bank.
        """
        pass
    
    def remove_user(self, id: int) -> User:
        """
        Removes a user from the bank.

        Args:
            id (int): ID of the user to remove.
        
        Raises:
            KeyError: ID not found in the list of users.

        Returns:
            User: The user removed from the bank.
        """
        pass

    def remove_account(self, id: int) -> Checking_Account:
        """
        Removes an account from the bank.

        Args:
            id (int): ID of the account to remove.
        
        Raises:
            KeyError: ID not found in the list of accounts.

        Returns:
            Checking_Account: The account removed from the bank.
        """
        pass
    


    





    

