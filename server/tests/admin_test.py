import pytest
from server.src.teller import Teller
from server.src.customer import Customer
from server.src.admin import Admin
from server.src.checking_account import CheckingAccount
from server.src.exceptions.account_frozen_exception import AccountFrozenException

class TestAdmin:
    def test_get_name(self):
        test = Admin("john", 5, "password")
        assert test.get_name() == "john"
    
    def test_get_id(self):
        test = Admin("john", 5, "password")
        assert test.get_id() == 5

    def test_get_password(self):
        test = Admin("john", 5, "password")
        assert test.get_passwd() == "password"

    def test_get_acc_type(self):
        test = Admin("john", 5, "password")
        assert test.get_accType() == 2

    def test_get_user_acc_details(self):
        test = Admin("john", 5, "password")
        assert test.get_user_acc_details() == ('Name:', 'john' , '\nID:', 5 , '\naccType: Admin')

    def test_check_sus_activity(self):
        #TODO: not sure if this is how we're checking it
        test = Admin("john", 5, "password")
        acc = CheckingAccount(4,50000.00)
        acc2 = CheckingAccount(2,50000.00)
        acc.withdraw(25000)
        acc2.withdraw(100)
        assert test.check_sus_activity(acc) == True
        assert test.check_sus_activity(acc2) == False


    def test_toggle_frozen(self):
        with pytest.raises(AccountFrozenException):
            test = Admin("john", 5, "password")
            acc = CheckingAccount(1,100)
            test.toggle_frozen(acc)
            acc.deposit(100)
        