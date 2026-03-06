import sys
sys.path.append('./server/src')

from teller import Teller
from checking_account import CheckingAccount

class Admin(Teller):
    def __init__(self, name, id, passwd):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.permissions = 2
        self.accounts = []
    
    """
    returns name, id, and customer in visual string
    """
    def get_user_acc_details(self):
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Admin"
    
    
    """
    checks a given account for suspicious activity based on withdrawal amounts
    PARAMS:
    acc - the account to check for suspicious activity
    """
    def check_sus_activity(self, acc : CheckingAccount):
        pass


    """
    freezes an account
    PARAMS:
    acc - the account to freeze
    """
    def toggle_frozen(self, acc : CheckingAccount):
        pass
