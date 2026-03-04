from abc import ABC, abstractmethod
class User(ABC):
    """
    A basic abstract class for all types of users.

    Attributes:
        id (int): account id number
        name (string): the name of the account
        password (string): account password
        accType (string): type of user account (e.g. admin, customer, or teller)
    """

    """
    Abstract Property
    """
    @property
    @abstractmethod
    def name(self):
        pass


    """
    Abstract Property
    """
    @property
    @abstractmethod
    def password(self):
        pass


    """
    Abstract Property    
    """
    @property
    @abstractmethod
    def id(self):
        pass


    """
    Abstract Property
    """
    @property
    @abstractmethod
    def accType(self):
        pass


    """
    returns all details of the account (e.g. account info, bank accounts held, etc), depending on the type of account. 
    """
    @abstractmethod
    def getAccDetails(self):
        pass