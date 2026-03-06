import sys
sys.path.append('./server/src')

from checking_account import CheckingAccount

class Customer():
    
    def __init__(self, name, id, passwd, bank):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.permissions = 0
        self.accounts = []
        self.bank = bank


    def get_name(self):
        return self.name
    

    def set_name(self, name:str):
        self.name = name


    def get_id(self):
        return self.id
    

    def set_id(self, id:int):
        self.id = id


    def get_passwd(self):
        return self.passwd
    

    def set_passwd(self, pss:str):
        self.passwd = pss


    def get_permissions(self):
        return self.permissions


    def get_accounts(self):
        return self.accounts

    
    def register_account(self, account: CheckingAccount):
        self.accounts.append(account)
        
    """
    returns name, id, and customer in visual string
    """
    def get_user_acc_details(self):
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Customer"

    """
    returns a formatted string containing all transactions in an accounts history
    """
    def get_total_transact_hist(self):
        result = ""
        for acc in self.accounts:
            result.append(acc.get_all_transaction_str())
            result.append("\n")
        return result