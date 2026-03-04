from abc import ABC, abstractmethod
from server.src.bank import Bank
class User(ABC):
    """
    A basic abstract class for all types of users.

    Attributes:
        id (int): account id number
        name (string): the name of the account
        password (string): account password
        accType (int): type of user account (e.g. admin(2), customer(0) , or teller(1))
        bank (Bank): bank the user belongs to 
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
    def acc_type(self):
        pass


    """
    returns all details of the account (e.g. account info, bank accounts held, etc), depending on the type of account. 
    """
    @abstractmethod
    def get_acc_details(self):
        pass