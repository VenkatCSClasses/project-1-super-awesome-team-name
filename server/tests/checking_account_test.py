from server.src.checking_account import CheckingAccount
from server.src.transaction import Transaction
import pytest


class TestCheckingAccount:

    def test_initial_balance(self):
        """
        Test that the initial balance of the checking account is set correctly.
        """
        account = CheckingAccount(1, balance=100.00)
        assert account.check_balance() == 100.00


    def test_withdraw(self):
        """
        Test that withdrawing from the checking account updates the balance correctly.
        """
        account = CheckingAccount(1, balance=100)
        account.withdraw(30)
        assert account.check_balance() == 70
        account.withdraw(20)
        assert account.check_balance() == 50
        account.withdraw(50)
        assert account.check_balance() == 0
        with pytest.raises(Exception):
            account.withdraw(10)  # Should raise an exception for insufficient funds

    def test_deposit(self):
        """
        Test that depositing into the checking account updates the balance correctly.
        """
        account = CheckingAccount(1, balance=100)
        account.deposit(50)
        assert account.check_balance() == 150
        account.deposit(25) 
        assert account.check_balance() == 175
        pytest.raises(Exception, account.deposit, -10)  # Should raise an exception for negative deposit
        pytest.raises(Exception, account.deposit, 0.000001)  # Should raise an exception for depositing more than 2 decimal places
    
    def test_transfer(self):
        """
        Test that transferring between two checking accounts updates both balances correctly.
        """
        account1 = CheckingAccount(1, balance=100)
        account2 = CheckingAccount(2, balance=50)
        account1.transfer(30, account2)
        assert account1.check_balance() == 70
        assert account2.check_balance() == 80
        
        pytest.raises(Exception, account1.transfer, 100, account2)  # Should raise an exception for insufficient funds
        pytest.raises(Exception, account1.transfer, -10, account2)  # Should raise an exception for negative transfer amount
        pytest.raises(Exception, account1.transfer, 0.000001, account2)  # Should raise an exception for transferring more than 2 decimal places

    def test_frozen_account(self):
        """
        Test that a frozen account does not allow withdrawals or transfers.
        """
        account1 = CheckingAccount(1, balance=100)
        account2 = CheckingAccount(2, balance=50)
        account1.toggle_frozen()  # Freeze account1
        assert account1.is_frozen() == True
        with pytest.raises(Exception):
            account1.withdraw(30)
        with pytest.raises(Exception):
            account1.transfer(30, account2)

    def test_unfreeze_account(self):
        """
        Test that an unfrozen account allows withdrawals and transfers.
        """
        account1 = CheckingAccount(1, balance=100)
        account2 = CheckingAccount(2, balance=50)
        account1.toggle_frozen()  # Freeze account1
        account1.toggle_frozen()  # Unfreeze account1
        assert account1.is_frozen() == False
        account1.withdraw(30)
        assert account1.check_balance() == 70
        account1.transfer(30, account2)
        assert account1.check_balance() == 40
        assert account2.check_balance() == 80

    def test_get_acct_num(self):
        """
        Test that the account number is returned correctly.
        """
        account = CheckingAccount(12345)
        assert account.get_acct_num() == 12345

    def test_get_acct_num_invalid(self):
        """
        Test that an invalid account number raises an exception.
        """
        with pytest.raises(Exception):
            CheckingAccount(-1)  # Should raise an exception for negative account number
    
    def test_get_transaction(self):
        """
        Test that retrieving a transaction by its number returns the correct transaction.
        """
        account = CheckingAccount(1, balance=100)
        account.deposit(50)  # Transaction 1
        account.withdraw(30)  # Transaction 2
        transaction = account.get_transaction(1)
        assert transaction.amount == 50
        assert transaction.type == 'deposit'
        transaction = account.get_transaction(2)
        assert transaction.amount == 30
        assert transaction.type == 'withdrawal'

    def test_get_transaction_invalid(self):
        """
        Test that retrieving a transaction with an invalid number raises an exception.
        """
        account = CheckingAccount(1, balance=100)
        with pytest.raises(Exception):
            account.get_transaction(999)  # Should raise an exception for non-existent transaction number

    def test_get_all_transactions(self):
        """
        Test that the transaction history is returned correctly.
        """
        account = CheckingAccount(1, balance=100)
        account.deposit(50)  # Transaction 1
        account.withdraw(30)  # Transaction 2
        history = account.get_all_transactions()
        assert len(history) == 2
        assert history[0].amount == 50
        assert history[0].type == 'deposit'
        assert history[1].amount == 30
        assert history[1].type == 'withdrawal'

    

    
    

    