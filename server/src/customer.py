class Customer():
    def __init__(self, name, id, passwd):
        self.name = name
        self.id = id
        self.passwd = passwd
        self.accType = 0
        self.accounts = []

    def get_name(self):
        return self.name
    
    def set_name(self, name:str):
        self.name = name


    def get_id(self):
        return self.id
    
    def set_id(self, id:int):
        self.int = self.int


    def get_passwd(self):
        return self.passwd
    
    def set_passwd(self, pss:str):
        self.passwd = pss


    def get_accType(self):
        return self.accType
    
    def set_accType(self, type:int):
        self.accType = type


    def get_accounts(self):
        return self.accounts
        
    """
    returns name, id, and customer in visual string
    """
    def get_acc_details(self):
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Customer"

    """
    returns a formatted string containing all transactions in an accounts history
    """
    def get_total_transact_hist(self):
        pass
    #TODO finish method above