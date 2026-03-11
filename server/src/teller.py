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
        accounts (dict): All accounts within the bank
        bank (Bank): The bank the teller belongs to
    """
    def __init__(self, name, id, passwd, bank):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.permissions = 1
        self.accounts = bank.get_all_accounts()
        self.bank = bank


    
    def get_user_acc_details(self):
        """
        returns name, id, and teller in visual string
        """
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Teller"


    
    def create_account(self, owner: Customer, isChecking : bool):
        """
        adds a checking or savings account to a given customer's account list

        Args:
            owner - the customer to add the acc to
            isChecking - determines what type of account to add
        """
        if (isChecking):
            self.accounts.create_account_for_user(owner, "checking")
        else:
            self.accounts.create_account_for_user(owner, "savings")

    
    def close_account(self, owner : Customer, acc : CheckingAccount):
        """
        removes a checking or savings account from a given customer's account list

        Args:
            owner - the customer to remove the acc from
            acc - the account to remove
        """
        for account in owner.getAccounts():
            if acc.get_acct_num() == account.get_acct_num():
                owner.get_accounts.remove(account)
                break

        for account in self.accounts():
            if acc.get_acct_num() == account.get_acct_num():
                self.accounts.remove(account)
                break
        