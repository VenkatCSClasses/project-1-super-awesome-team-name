import sys
sys.path.append('./server/src')

from checking_account import CheckingAccount
from bank import Bank
from exceptions.account_frozen_exception import AccountFrozenException
from exceptions.amount_invalid_exception import AmountInvalidException
from exceptions.insufficient_funds_exception import InsufficientFundsException
from transaction_type import TransactionType

import pytest

class TestCheckingAccount:

    def test_initial_balance_check_balance(self):
        """Test that the initial balance of the checking account is set correctly."""
        bank = Bank()
        account = CheckingAccount(1, bank, balance=100.00)
        assert account.check_balance() == 100.00
        with pytest.raises(AmountInvalidException):
            account = CheckingAccount(1, bank, -0.01)
        with pytest.raises(AmountInvalidException):
            account = CheckingAccount(1, bank, 10.111)


    def test_withdraw(self):
        """Test that withdrawing from the checking account updates the balance correctly."""
        bank = Bank()
        account = CheckingAccount(1, bank, balance=100)
        account.withdraw(30)
        assert account.check_balance() == 70
        account.withdraw(20)
        assert account.check_balance() == 50
        account.withdraw(50)
        assert account.check_balance() == 0
        with pytest.raises(InsufficientFundsException):
            account.withdraw(10)  # Should raise an exception for insufficient funds


    def test_deposit(self):
        """Test that depositing into the checking account updates the balance correctly."""
        bank = Bank()
        account = CheckingAccount(1, bank, balance=100)
        account.deposit(50)
        assert account.check_balance() == 150
        account.deposit(25) 
        assert account.check_balance() == 175
        pytest.raises(AmountInvalidException, account.deposit, -10)  # Should raise an exception for negative deposit
        pytest.raises(AmountInvalidException, account.deposit, 0.000001)  # Should raise an exception for depositing more than 2 decimal places
    

    def test_transfer(self):
        """Test that transferring between two checking accounts updates both balances correctly."""
        bank = Bank()
        account1 = CheckingAccount(1, bank, balance=100)
        account2 = CheckingAccount(2, bank, balance=50)
        account1.transfer(30, account2)
        assert account1.check_balance() == 70
        assert account2.check_balance() == 80
        
        pytest.raises(InsufficientFundsException, account1.transfer, 100, account2)  # Should raise an exception for insufficient funds
        pytest.raises(AmountInvalidException, account1.transfer, -10, account2)  # Should raise an exception for negative transfer amount
        pytest.raises(AmountInvalidException, account1.transfer, 0.000001, account2)  # Should raise an exception for transferring more than 2 decimal places


    def test_frozen_account(self):
        """Test that a frozen account does not allow withdrawals, transfers, and deposit."""
        bank = Bank()
        account1 = CheckingAccount(1, bank, balance=100)
        account2 = CheckingAccount(2, bank, balance=50)
        account1.toggle_frozen()  # Freeze account1
        assert account1.is_frozen()
        with pytest.raises(AccountFrozenException):
            account1.withdraw(30)
        with pytest.raises(AccountFrozenException):
            account1.transfer(30, account2)
        with pytest.raises(AccountFrozenException):
            account1.deposit(30)


    def test_unfreeze_account(self):
        """Test that an unfrozen account allows withdrawals, transfers, and deposit"""
        bank = Bank()
        account1 = CheckingAccount(1, bank, balance=100)
        account2 = CheckingAccount(2, bank, balance=50)
        account1.toggle_frozen()  # Freeze account1
        account1.toggle_frozen()  # Unfreeze account1
        assert not account1.is_frozen()
        account1.withdraw(30)
        assert account1.check_balance() == 70
        account1.transfer(30, account2)
        assert account1.check_balance() == 40
        assert account2.check_balance() == 80
        account1.deposit(30)
        assert account1.check_balance() == 70


    def test_get_account_id(self):
        """Test that the account number is returned correctly."""
        bank = Bank()
        account = CheckingAccount(12345, bank)
        assert account.get_account_id() == 12345
    

    def test_get_transaction(self):
        """Test that retrieving a transaction by its number returns the correct transaction."""
        bank = Bank()
        account = CheckingAccount(1, bank, balance=100)
        account.deposit(50)  # Transaction ID 2
        account.withdraw(30)  # Transaction ID 3
        transaction = account.get_transaction(2, True)
        assert transaction.get_amount() == 50
        assert transaction.get_account_id() == 1
        assert transaction.get_relative_id() == 2
        assert transaction.get_post_balance() == 150
        transaction = account.get_transaction(3, True)
        assert transaction.get_amount() == -30
        assert transaction.get_account_id() == 1
        assert transaction.get_relative_id() == 3
        assert transaction.get_post_balance() == 120


    def test_log_transaction(self):
        bank = Bank()
        account = CheckingAccount(1, bank, balance=100)
        account.log_transaction(50, TransactionType.DEPOSIT)
        account.log_transaction(-50, TransactionType.TRANSFER_WITHDRAW, 3)
        transaction = account.get_transaction(2, True)
        assert transaction.get_amount() == 50
        assert transaction.get_type() == TransactionType.DEPOSIT
        assert transaction.get_transfer_account_id() is None
        transaction = account.get_transaction(3, True)
        assert transaction.get_amount() == -50
        assert transaction.get_type() == TransactionType.TRANSFER_WITHDRAW
        assert transaction.get_transfer_account_id() == 3


    def test_get_transaction_invalid(self):
        """
        Test that retrieving a transaction with an invalid number raises an exception.
        """
        bank = Bank()
        account = CheckingAccount(1, bank, balance=100)
        with pytest.raises(KeyError):
            account.get_transaction(999)  # Should raise an exception for non-existent transaction number


    def test_get_all_transactions(self):
        """Test that the transaction history is returned correctly."""
        bank = Bank()
        account = CheckingAccount(1, bank, balance=100)
        account.deposit(50)  # Transaction ID 2
        account.withdraw(30)  # Transaction ID 3
        history = account.get_all_transactions()
        assert len(history) == 3
        assert history.get(2).get_account_id() == 1
        assert history.get(3).get_account_id() == 1
        assert history.get(2).get_relative_id() == 2
        assert history.get(3).get_relative_id() == 3
        assert history.get(2).get_amount() == 50
        assert history.get(3).get_amount() == -30
        assert history.get(2).get_post_balance() == 150
        assert history.get(3).get_post_balance() == 120

    def test_is_amount_valid(self):
        """Tests to see if an amount is valid (non-negative and 2 or less decimal places)"""
        assert CheckingAccount._is_amount_valid(10) 
        assert CheckingAccount._is_amount_valid(10.01)
        assert CheckingAccount._is_amount_valid(0.01)
    
        assert not CheckingAccount._is_amount_valid(0) 
        assert not CheckingAccount._is_amount_valid(-10) 
        assert not CheckingAccount._is_amount_valid(-10.001)
        assert not CheckingAccount._is_amount_valid(0.001) 
        assert not CheckingAccount._is_amount_valid(0.11111111) 