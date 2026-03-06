import sys
sys.path.append("./server/src")

from savings_account import SavingsAccount
from checking_account import CheckingAccount
from exceptions.account_frozen_exception import AccountFrozenException
from exceptions.amount_invalid_exception import AmountInvalidException
from exceptions.insufficient_funds_exception import InsufficientFundsException
from exceptions.withdraw_maxed_exception import WithdrawMaxedException

import pytest
import os

from dotenv import load_dotenv
load_dotenv()

class TestSavingsAccount:

    def test_constructor_getters(self):
        """Tests covering the constructor and the accessors of the savingsaccount"""
        acc0 = SavingsAccount(0)
        acc1 = SavingsAccount(1, 100)

        assert acc0.check_balance() == 0
        assert acc1.check_balance() == 100
        assert acc0.get_acct_num() == 0
        assert acc1.get_acct_num() == 1

        assert acc0.get_interest_amount == os.getenv("DAILY_INTEREST", 0.05)
        assert acc1.get_interest_amount == os.getenv("DAILY_INTEREST", 0.05)
        assert acc1.get_interest_amount == os.getenv("MAX_WITHDRAW_LIMIT", 10000)
        assert acc1.get_interest_amount == os.getenv("MAX_WITHDRAW_LIMIT", 10000)
    
    def test_withdraw_limit(self):
        """Tests covering the updated withdraw method and ensuring withdraw limit is changed"""
        acc0 = SavingsAccount(0, os.getenv("MAX_WITHDRAW_LIMIT", 10000) + 200)
        acc0.withdraw(200)

        assert acc0.get_current_withdraw_limit == os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 200
        assert acc0.check_balance == os.getenv("MAX_WITHDRAW_LIMIT", 10000)

        acc0.withdraw(os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 200)
        
        assert acc0.get_current_withdraw_limit == 0
        assert acc0.check_balance == 200

        with pytest.raises(WithdrawMaxedException):
            acc0.withdraw(10)
    
    def test_transfer_limit(self):
        """Tests covering the updated transfer method and ensuring withdraw limit is changed"""
        acc0 = SavingsAccount(0, os.getenv("MAX_WITHDRAW_LIMIT", 10000) + 200)
        acc1 = SavingsAccount(1)
        acc0.transfer(200, acc1)

        assert acc0.get_current_withdraw_limit == os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 200
        assert acc0.check_balance == os.getenv("MAX_WITHDRAW_LIMIT", 10000)

        acc0.transfer(os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 200, acc1)
        
        assert acc0.get_current_withdraw_limit == 0
        assert acc0.check_balance == 200

        with pytest.raises(WithdrawMaxedException):
            acc0.transfer(10, acc1)

    def test_compound_interest(self):
        """Tests covering the compound interest method"""


    def test_reset_withdraw_limit(self):
        """Tests covering resetting the withdraw limit"""


