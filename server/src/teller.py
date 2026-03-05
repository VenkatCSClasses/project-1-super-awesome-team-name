from server.src.customer import Customer
from server.src.checking_account import CheckingAccount


class Teller(Customer):
    def __init__(self, name, id, passwd):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.accType = 1
        self.accounts = []


    """
    returns name, id, and teller in visual string
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
            #TODO owner.get_accounts().append(new CheckingAccount())
            pass
        else:
            #TODO owner.get_accounts().append(new SavingsAccount())
            pass

    """
    removes a checking or savings account from a given customer's account list

    PARAMS:
    owner - the customer to remove the acc from
    acc - the account to remove
    """
    def close_account(self, owner : Customer, acc : CheckingAccount):
        pass
        """
        for account in owner.getAccounts():
            if acc.get_acct_num() == account.get_acct_num():
                owner.get_accounts.remove(account)
                break

        """
        