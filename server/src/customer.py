from .user import User

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
    def accType(self):
        return self.accType
    
    def getAccDetails(self):
        return "Name:" , self.name , "\nID:" , self.id , "\naccType: Customer"
    
    def getAccounts(self):
        return self.accounts

    def getTotalTransactHist(self):
        pass
    #TODO finish method above