import sys
sys.path.append('./server/src')

from teller import Teller
from checking_account import CheckingAccount
from transaction import Transaction

class Admin(Teller):
    """
    A class used to represent an admin account within the bank

    Attributes:
        name (str): The name of the account
        id (int): The unique ID of the account
        passwd (str): The password of the account
        permissions (int): The permission level of the account
        accounts (dict): All accounts within the bank
        bank (Bank): The bank the teller belongs to
    """
    def __init__(self, name, id, passwd, bank):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.permissions = 2
        self.accounts = bank.get_all_accounts()
        self.bank = bank
    
    
    def get_user_acc_details(self):
        """
        returns name, id, and customer in visual string
        """
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Admin"
    
    
    def check_sus_activity(self, acc):
        """
        checks a given account for suspicious activity based on withdrawal amounts;
        returns true if a single transaction has withdrawn $10,000 or more, false otherwise
        
        Args:
            acc - the account to check for suspicious activity
        """
        for transact in acc.get_all_transactions():
            if transact.get_amount() <= -10000:
                return True
        return False

    def check_all_sus_activity(self):
        """
        returns a list of all accounts within the bank that have a suspicious transaction
        """
        sus_accounts = []
        for acc in self.accounts:
            if self.check_sus_activity(acc):
                sus_accounts.append(acc)
        return sus_accounts

    def toggle_frozen(self, acc):
        """
        freezes an account
        
        Args:
            acc - the account to freeze
        """
        acc.toggle_frozen()
