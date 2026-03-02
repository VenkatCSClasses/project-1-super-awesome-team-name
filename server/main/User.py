from abc import ABC, abstractmethod

class User(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def password(self):
        pass

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def accType(self):
        pass

    @abstractmethod
    def getAccDetails(self):
        pass