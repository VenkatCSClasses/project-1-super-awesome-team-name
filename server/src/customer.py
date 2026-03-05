from server.src.user import User

class Customer(User):
    def __init__(self, name, id, passwd):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.accType = 0
        self.accounts = []

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
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Customer"
    
    """
    returns the customer's accounts
    """
    def get_accounts(self):
        return self.accounts

    """
    returns a formatted string containing all transactions in an accounts history
    """
    def get_total_transact_hist(self):
        pass
    #TODO finish method above