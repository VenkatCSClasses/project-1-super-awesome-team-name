import sys
import pytest
sys.path.append('./server/src')

from admin import Admin
from checking_account import CheckingAccount
from exceptions.account_frozen_exception import AccountFrozenException

class TestAdmin:
    
    def test_get_name(self):
        test = Admin("john", 5, "password", None)
        assert test.get_name() == "john"
    
    def test_get_id(self):
        test = Admin("john", 5, "password", None)
        assert test.get_id() == 5

    def test_get_password(self):
        test = Admin("john", 5, "password", None)
        assert test.get_passwd() == "password"

    def test_get_permissions(self):
        test = Admin("john", 5, "password", None)
        assert test.get_permissions() == 2

    def test_get_user_acc_details(self):
        test = Admin("john", 5, "password", None)
        assert test.get_user_acc_details() == ('Name:', 'john' , '\nID:', 5 , '\naccType: Admin')

    def test_check_sus_activity(self):
        #TODO: not sure if this is how we're checking it
        test = Admin("john", 5, "password", None)
        acc = CheckingAccount(4,50000.00)
        acc2 = CheckingAccount(2,50000.00)
        acc.withdraw(25000)
        acc2.withdraw(100)
        assert test.check_sus_activity(acc)
        assert test.check_sus_activity(acc2)


    def test_toggle_frozen(self):
        with pytest.raises(AccountFrozenException):
            test = Admin("john", 5, "password", None)
            acc = CheckingAccount(1,100)
            test.toggle_frozen(acc)
            acc.deposit(100)
        