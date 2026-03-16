import sys
sys.path.append("./server/src")

from savings_account import SavingsAccount
from bank import Bank
from exceptions.withdraw_maxed_exception import WithdrawMaxedException
from transaction_type import TransactionType

import pytest
import os
from pytest import approx # Added for looser comparisons

from dotenv import load_dotenv
load_dotenv()

class TestSavingsAccount:

    def test_constructor_getters(self):
        """Intergration Test: Tests covering the constructor and the accessors of the savingsaccount"""
        bank = Bank()
        acc0 = SavingsAccount(0, bank)
        acc1 = SavingsAccount(1, bank, 100)

        assert acc0.check_balance() == 0
        assert acc1.check_balance() == 100
        assert acc0.get_account_id() == 0
        assert acc1.get_account_id() == 1

        # Using approx here in case the env var has high precision
        interest = float(os.getenv("DAILY_INTEREST", 0.0005))
        assert acc0.get_interest_amount() == approx(interest)
        
        limit = float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
        assert acc1.get_max_withdraw_limit() == approx(limit)
        assert acc0.get_account_type() == "savings"
    

    def test_withdraw_limit(self):
        """Intergration Test: Tests covering the updated withdraw method and ensuring withdraw limit is changed"""
        bank = Bank()
        max_limit = float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
        acc0 = SavingsAccount(0, bank, max_limit + 200)
        acc0.withdraw(200)

        assert acc0.get_current_withdraw_limit() == approx(max_limit - 200)
        assert acc0.check_balance() == approx(max_limit)

        acc0.withdraw(max_limit - 200)
        
        assert acc0.get_current_withdraw_limit() == approx(0)
        assert acc0.check_balance() == approx(200)

        with pytest.raises(WithdrawMaxedException):
            acc0.withdraw(10)
    

    def test_transfer_limit(self):
        """Intergration Test: Tests covering the updated transfer method and ensuring withdraw limit is changed"""
        bank = Bank()
        max_limit = float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
        acc0 = SavingsAccount(0, bank, max_limit + 200)
        acc1 = SavingsAccount(1, bank)
        acc0.transfer(200, acc1)

        assert acc0.get_current_withdraw_limit() == approx(max_limit - 200)
        assert acc0.check_balance() == approx(max_limit)

        acc0.transfer(max_limit - 200, acc1)
        
        assert acc0.get_current_withdraw_limit() == approx(0)
        assert acc0.check_balance() == approx(200)


    def test_compound_interest(self):
        """Intergration Test: Tests covering the compound interest method and transaction logging"""
        bank = Bank()
        acc0 = SavingsAccount(0, bank, 100)
        acc1 = SavingsAccount(1, bank, 500)
        daily_interest = float(os.getenv("DAILY_INTEREST", 0.0005))

        acc0.compound_interest()
        acc1.compound_interest()

        # Calculation of expected amounts
        amount0 = round((1 + daily_interest) * 100, 2)
        amount1 = round((1 + daily_interest) * 500, 2)

        assert acc0.check_balance() == approx(amount0)
        assert acc1.check_balance() == approx(amount1)

        acc0.compound_interest()
        acc1.compound_interest()

        amount2 = round((1 + daily_interest) * amount0, 2)
        amount3 = round((1 + daily_interest) * amount1, 2)
 
        assert acc0.check_balance() == approx(amount2)
        assert acc1.check_balance() == approx(amount3)

        # LOOSE COMPARISONS FOR TRANSACTION AMOUNTS
        assert acc0.get_transaction(3).get_amount() == approx(amount0 - 100)
        assert acc1.get_transaction(4).get_amount() == approx(amount1 - 500)
        assert acc0.get_transaction(5).get_amount() == approx(amount2 - amount0)
        assert acc1.get_transaction(6).get_amount() == approx(amount3 - amount1)

        assert acc0.get_transaction(3).get_type() == TransactionType.INTEREST
        assert acc1.get_transaction(4).get_type() == TransactionType.INTEREST


    def test_reset_withdraw_limit(self):
        """Intergration Tests: Tests covering resetting the withdraw limit"""
        bank = Bank()
        max_limit = float(os.getenv("MAX_WITHDRAW_LIMIT", 10000))
        acc0 = SavingsAccount(0, bank, 50)
        acc1 = SavingsAccount(1, bank, 100)

        acc0.withdraw(20)
        acc1.withdraw(50)

        assert acc0.get_current_withdraw_limit() == approx(max_limit - 20)
        assert acc1.get_current_withdraw_limit() == approx(max_limit - 50)

        acc0.reset_withdraw_limit()
        acc1.reset_withdraw_limit()

        assert acc0.get_current_withdraw_limit() == approx(max_limit)
        assert acc1.get_current_withdraw_limit() == approx(max_limit)