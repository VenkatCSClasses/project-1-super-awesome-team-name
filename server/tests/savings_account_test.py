import sys
sys.path.append("./server/src")

from savings_account import SavingsAccount
from bank import Bank
from exceptions.withdraw_maxed_exception import WithdrawMaxedException

import pytest
import os

from dotenv import load_dotenv
load_dotenv()

class TestSavingsAccount:

    def test_constructor_getters(self):
        """Tests covering the constructor and the accessors of the savingsaccount"""
        bank = Bank()
        acc0 = SavingsAccount(0, bank)
        acc1 = SavingsAccount(1, bank, 100)

        assert acc0.check_balance() == 0
        assert acc1.check_balance() == 100
        assert acc0.get_acct_num() == 0
        assert acc1.get_acct_num() == 1

        assert acc0.get_interest_amount() == float(os.getenv("DAILY_INTEREST", 0.05))
        assert acc1.get_interest_amount() == float(os.getenv("DAILY_INTEREST", 0.05))
        assert acc1.get_max_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
        assert acc1.get_max_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
    

    def test_withdraw_limit(self):
        """Tests covering the updated withdraw method and ensuring withdraw limit is changed"""
        bank = Bank()
        acc0 = SavingsAccount(0, bank, float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)) + 200)
        acc0.withdraw(200)

        assert acc0.get_current_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)) - 200
        assert acc0.check_balance() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))

        acc0.withdraw(float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)) - 200)
        
        assert acc0.get_current_withdraw_limit() == 0
        assert acc0.check_balance() == 200

        with pytest.raises(WithdrawMaxedException):
            acc0.withdraw(10)
    

    def test_transfer_limit(self):
        """Tests covering the updated transfer method and ensuring withdraw limit is changed"""
        bank = Bank()
        acc0 = SavingsAccount(0, bank, float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)) + 200)
        acc1 = SavingsAccount(1, bank)
        acc0.transfer(200, acc1)

        assert acc0.get_current_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 200)
        assert acc0.check_balance() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))

        acc0.transfer(float(os.getenv("MAX_WITHDRAW_LIMIT", 10000) - 200), acc1)
        
        assert acc0.get_current_withdraw_limit() == 0
        assert acc0.check_balance() == 200

        with pytest.raises(WithdrawMaxedException):
            acc0.transfer(10, acc1)


    def test_compound_interest(self):
        """Tests covering the compound interest method and transaction logging"""
        bank = Bank()
        acc0 = SavingsAccount(0, bank, 100)
        acc1 = SavingsAccount(1, bank, 500)

        acc0.compound_interest()
        acc1.compound_interest()

        amount0 = round((1 + float(os.getenv("DAILY_INTEREST", 0.05))) * 100, 2)
        amount1 = round((1 + float(os.getenv("DAILY_INTEREST", 0.05))) * 500, 2)

        assert acc0.check_balance() == amount0
        assert acc1.check_balance() == amount1

        acc0.compound_interest()
        acc1.compound_interest()

        amount2 = round((1 + float(os.getenv("DAILY_INTEREST", 0.05))) * amount0, 2)
        amount3 = round((1 + float(os.getenv("DAILY_INTEREST", 0.05))) * amount1, 2)
 
        assert acc0.check_balance() == amount2
        assert acc1.check_balance() == amount3

        assert amount0 == acc0.get_transaction(0)
        assert amount1 == acc1.get_transaction(1)
        assert amount2 == acc0.get_transaction(2)
        assert amount3 == acc1.get_transaction(3)




    def test_reset_withdraw_limit(self):
        """Tests covering resetting the withdraw limit"""
        bank = Bank()
        acc0 = SavingsAccount(0, bank, 50)
        acc1 = SavingsAccount(1, bank, 100)

        acc0.withdraw(20)
        acc1.withdraw(50)

        assert acc0.get_current_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)) - 20
        assert acc1.get_current_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)) - 50

        acc0.reset_withdraw_limit()
        acc1.reset_withdraw_limit()

        assert acc0.get_current_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000)) 
        assert acc1.get_current_withdraw_limit() == float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
