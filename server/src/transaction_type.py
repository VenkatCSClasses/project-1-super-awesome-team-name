import sys
sys.path.append('./server/src')

from enum import Enum

class TransactionType(Enum):
    """
    Class used as an enumerator to allow easy pass-through of data regarding types of transactions.
    """

    WITHDRAW = 1
    DEPOSIT = 2
    TRANSFER_WITHDRAW = 3
    TRANSFER_DEPOSIT = 4
    NEW_ACCOUNT = 5