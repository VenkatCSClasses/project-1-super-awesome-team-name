from user import User
from checking_account import CheckingAccount

class Admin(User):
    def __init__(self, name, id, passwd):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.accType = 2

    @property
    def name(self):
        return self.name
    
    @property
    def id(self):
        return self.id

    @property  
    def password(self):
        return self.passwd
    
    @property
    def acc_type(self):
        return self.accType
    
    
    def get_acc_details(self):
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
