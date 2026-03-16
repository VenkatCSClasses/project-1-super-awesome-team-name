import sys
import pytest
sys.path.append('./server/src')

from bank import Bank
from admin import Admin
from checking_account import CheckingAccount
from exceptions.account_frozen_exception import AccountFrozenException

class TestAdmin:
    
    def test_get_name(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Admin("john", 5, "password", bank)
        assert test.get_name() == "john"
    
    def test_get_id(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Admin("john", 5, "password", bank)
        assert test.get_id() == 5

    def test_get_password(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Admin("john", 5, "password", bank)
        assert test.get_passwd() == "password"

    def test_get_permissions(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Admin("john", 5, "password", bank)
        assert test.get_permissions() == 2

    def test_get_user_acc_details(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Admin("john", 5, "password", bank)
        assert test.get_user_acc_details() == ('Name:', 'john' , '\nID:', 5 , '\naccType: Admin')

    def test_check_sus_activity(self):
        """integration test: tests varying levels of withdrawals to determine effective flagging"""
        bank = Bank()
        test = Admin("john", 5, "password", bank)
        acc = CheckingAccount(4, bank, 50000.00)
        acc2 = CheckingAccount(2, bank, 50000.00)
        acc.withdraw(25000)
        acc2.withdraw(100)
        assert test.check_sus_activity(acc)
        assert test.check_sus_activity(acc2)

    def test_toggle_frozen(self):
        """integration test: ensures freeze effect is applied at the correct times"""
        bank = Bank()
        test = Admin("john", 5, "password", bank)
        acc = CheckingAccount(1, bank, 100)
        test.toggle_frozen(acc)
        with pytest.raises(AccountFrozenException):
            acc.deposit(100)
        test.toggle_frozen(acc)
        acc.deposit(100)
        assert acc.check_balance() == 200