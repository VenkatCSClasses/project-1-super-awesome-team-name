import sys
import datetime
sys.path.append('./server/src')

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from checking_account import CheckingAccount

class Customer():
    
    def __init__(self, name, id, passwd, bank, permissions=0):
        """
        A class used to represent an customer account within the bank

        Attributes:
            name (str): The name of the account
            id (int): The unique ID of the account
            passwd (str): The password of the account
            permissions (int): The permission level of the account
            accounts (dict): All accounts owned by the customer
            bank (Bank): The bank the customer belongs to
        """
        self.name = name
        self.id = id
        self.passwd = passwd
        self.permissions = permissions
        self.accounts = {}
        self.bank = bank

    def get_name(self):
        """returns the customer's name"""
        return self.name
    

    def set_name(self, name:str):
        """
        sets the customer's name

        Args:
        name (str): the new name for the customer
        """
        self.name = name


    def get_id(self):
        """returns the customer's id"""
        return self.id
    

    def set_id(self, id:int):
        """
        sets the customer's id

        Args:
        id (id): the new id for the customer
        """
        self.id = id


    def get_passwd(self):
        """returns the customer's password"""
        return self.passwd
    

    def set_passwd(self, pss:str):
        """
        sets the customer's password

        Args:
        pss (str): the new password for the customer
        """
        self.passwd = pss


    def get_permissions(self):
        """returns the customer's permissions"""
        return self.permissions


    def get_accounts(self):
        """returns the customer's accounts"""
        return self.accounts

    def get_owned_accounts(self):
        """Returns only the accounts explicitly owned by this user."""
        return self.accounts

    
    def register_account(self, account: CheckingAccount):
        """
        adds the passed in account to the account dictionary

        Args:
        account (CheckingAccount): the account to add
        
        """
        self.accounts[account.get_account_id()] = account
        
    
    def get_user_acc_details(self):
        """
        returns name, id, and customer in visual string
        """
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Customer"

    
    def get_total_transact_hist(self):
        """
        returns a formatted string containing all transactions in an accounts history
        """
        total_hist = {} 

        for acc in self.accounts.values():
            for transaction in acc.get_all_transactions().values():
                total_hist[transaction.get_absolute_id()] = transaction
            
        return total_hist
