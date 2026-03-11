import sys
sys.path.append('./server/src')

from customer import Customer
from checking_account import CheckingAccount
from bank import Bank


class TestBank:
    
    def test_add_user(self):
        """Test that a user can be added to the bank and is retrievable"""
        bank = Bank()
        assert len(bank.get_users()) == 0
        bank.add_user(Customer("john", 5, "password"))
        assert len(bank.get_users()) == 1
        assert bank.find_user_by_id(5) == Customer("john", 5, "password")

    def test_remove_user(self):
        """Test that a user can be removed from the bank and is no longer retrievable"""
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert len(bank.get_users()) == 1
        bank.remove_user(user)
        assert len(bank.get_users()) == 0
        assert bank.find_user_by_id(5) is None


    def test_remove_user_by_name(self):
        """Test that a user can be removed from the bank by name and is no longer retrievable"""
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert len(bank.get_users()) == 1
        bank.remove_user_by_name("john")
        assert len(bank.get_users()) == 0
        assert bank.find_user_by_name("john") is None


    def test_remove_user_by_id(self):
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert len(bank.get_users()) == 1
        bank.remove_user_by_id(5)
        assert len(bank.get_users()) == 0
        assert bank.find_user_by_name("john") is None


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
        """Test that the total balance is correctly calculated if account balances change"""
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        assert bank.get_total_balance(user) == 0.0

        user = bank.get_user_by_id(5)
        account = CheckingAccount(1001, 1000.00)
        assert bank.get_total_balance(user) == 1000.00

    def test_get_next_transaction_id(self):
        """Test that get_next_transaction_ID works correctly"""
        bank = Bank()

        assert bank.get_next_transaction_id() == 1
        assert bank.get_next_transaction_id() == 2
        assert bank.get_next_transaction_id() == 3

    def test_remove_acc(self):
        """Test that bank accounts can be removed successfully"""
        bank = Bank()
        user = Customer("john", 5, "password")
        bank.add_user(user)
        bank.create_account_for_user(user)
        assert bank.get_all_accounts() != 0
        bank.remove_account(user.get_account_id())
        assert bank.get_all_accounts() == 0
        