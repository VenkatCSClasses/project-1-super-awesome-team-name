import sys
sys.path.append('./server/src')

from customer import Customer
from checking_account import CheckingAccount


class Teller(Customer):
    """
    A class used to represent a teller account within the bank

    Attributes:
        name (str): The name of the account
        id (int): The unique ID of the account
        passwd (str): The password of the account
        permissions (int): The permission level of the account
        bank (Bank): The bank the teller belongs to
    """
    def __init__(self, name, id, passwd, bank, permissions = 1):
        super().__init__(name, id, passwd, bank, permissions)


    
    def get_user_acc_details(self):
        """
        returns name, id, and teller in visual string
        """
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Teller"


    
    def create_account(self, owner: Customer, isChecking: bool):
        """
        adds a checking or savings account to a given customer's account list

        Args:
            owner - the customer to add the acc to
            isChecking - determines what type of account to add
        """
        if (isChecking):
            self.bank.create_account_for_user(owner, "CHECKING")
        else:
            self.bank.create_account_for_user(owner, "SAVINGS")

    
    def close_account(self, owner: Customer, account: CheckingAccount):
        """
        removes a checking or savings account from a given customer's account list

        Args:
            owner - the customer to remove the acc from
            account - the account to remove
        """
        owner.get_accounts().pop(account.get_account_id())
        
    def get_accounts(self):
        """Gets all accounts from bank attribute. Used to mitigate superclass get_accounts() as accounts is not a parameter of teller."""
        return self.bank.get_all_accounts()
