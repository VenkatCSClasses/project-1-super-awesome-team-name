import sys
sys.path.append("./server/src")

from savings_account import SavingsAccount
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
        acc0 = SavingsAccount(0, 100)
        acc1 = SavingsAccount(1, 500)

        acc0.compound_interest()
        acc1.compound_interest()

        assert acc0.check_balance() == (1 + os.getenv("DAILY_INTEREST", 0.05)) * 100
        assert acc1.check_balance() == (1 + os.getenv("DAILY_INTEREST", 0.05)) * 500

        acc0.compound_interest()
        acc1.compound_interest()

        assert acc0.check_balance() == ((1 + os.getenv("DAILY_INTEREST", 0.05)) * (1 + os.getenv("DAILY_INTEREST", 0.05))) * 100
        assert acc1.check_balance() == ((1 + os.getenv("DAILY_INTEREST", 0.05)) * (1 + os.getenv("DAILY_INTEREST", 0.05))) * 500


    def test_reset_withdraw_limit(self):
        """Tests covering resetting the withdraw limit"""
        acc0 = SavingsAccount(0, 50)
        acc1 = SavingsAccount(1, 100)

        acc0.withdraw(20)
        acc1.withdraw(50)

        assert acc0.get_current_withdraw_limit() == os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 20
        assert acc1.get_current_withdraw_limit() == os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 50

        acc0.reset_withdraw_limit()
        acc1.reset_withdraw_limit()

        assert acc0.get_current_withdraw_limit() == os.getenv("MAX_WITHDRAW_LIMIT", 10000) 
        assert acc1.get_current_withdraw_limit() == os.getenv("MAX_WITHDRAW_LIMIT", 10000) 
