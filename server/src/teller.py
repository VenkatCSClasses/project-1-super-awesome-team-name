from .user import User
from .customer import Customer
from .checking_account import CheckingAccount


class Teller(User):
    def __init__(self, name, id, passwd):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.accType = 1

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
    
    """
    returns name, id, and customer in visual string
    """
    def get_acc_details(self):
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Teller"

    """
    adds a checking or savings account to a given customer's account list

    PARAMS:
    owner - the customer to add the acc to
    isChecking - determines what type of account to add
    """
    def create_account(self, owner: Customer, isChecking : bool):
        if isChecking:
            #TODO owner.getAccounts().append(new CheckingAccount())
            pass
        else:
            #TODO owner.getAccounts().append(new SavingsAccount())
            pass

    """
    removes a checking or savings account from a given customer's account list

    PARAMS:
    owner - the customer to remove the acc from
    acc - the account to remove
    """
    def close_account(self, owner : Customer, acc : CheckingAccount):
        for account in owner.getAccounts():
            if acc.get_acct_num() == account.get_acct_num():
                owner.accounts.remove(account)
                break
