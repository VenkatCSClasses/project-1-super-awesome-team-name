import sys
sys.path.append('./server/src')

from customer import Customer
from checking_account import CheckingAccount
from bank import Bank


class TestBank:
    def test_add_user(self):
        bank = Bank()
        assert len(bank.get_users()) == 0
        bank.add_user(Customer("john", 5, "password"))
        assert len(bank.get_users()) == 1

    def test_remove_user(self):
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert len(bank.get_users()) == 1
        bank.remove_user(user)
        assert len(bank.get_users()) == 0


    def test_remove_user_by_name(self):
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert len(bank.get_users()) == 1
        bank.remove_user_by_name("john")
        assert len(bank.get_users()) == 0


    def test_remove_user_by_id(self):
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert len(bank.get_users()) == 1
        bank.remove_user_by_id(5)
        assert len(bank.get_users()) == 0


    def test_get_user_by_id(self):
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert bank.get_user_by_id(5) == user

    
    def test_get_user_by_name(self):
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert bank.get_user_by_name("john") == user
    

    def test_get_total_balance(self):
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert bank.get_total_balance(user) == 0.0

        user = bank.get_user_by_id(5)
        account = CheckingAccount(1001, 1000.00)
        assert bank.get_total_balance(user) == 1000.00