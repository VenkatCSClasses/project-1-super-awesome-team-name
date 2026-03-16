import sys
sys.path.append('./server/src')

from bank import Bank
from teller import Teller
from admin import Admin
from checking_account import CheckingAccount
from exceptions.account_frozen_exception import AccountFrozenException
import pytest

def test_system():
    # Create a bank 
    bank = Bank()

    # Customers should be able to create accounts
    bank.register_user("john bank", "123")
    customer = bank.get_user_by_name("john bank")
    assert customer.get_name() == "john bank" 
    bank.create_account_for_user(customer, "CHECKING", 500.00)
    bank.create_account_for_user(customer, "CHECKING", 0)

    # Assure the accounts were created with the proper information
    account = bank.get_account_by_id(1) 
    assert account.get_balance() == 500.00
    other_account = bank.get_account_by_id(2)
    assert other_account.get_balance() == 0.00

    # Test a transfer
    account.transfer(100.00, other_account)
    assert account.get_balance() == 400.00
    assert other_account.get_balance() == 100.00

    # Register another customer to test transfers between accounts of different customers
    bank.register_user("bob banks", "321")
    other_customer = bank.get_user_by_name("bob banks")
    assert other_customer.get_name() == "bob banks"
    bank.create_account_for_user(other_customer, "CHECKING", 0)
    other_account_2 = bank.get_account_by_id(3)
    assert other_account_2.get_balance() == 0.00

    account.transfer(50.00, other_account_2)
    assert account.get_balance() == 350.00
    assert other_account_2.get_balance() == 50.00

    # Assure that tellers can create accounts for customers
    teller = Teller("teller", 3, "password", bank)
    bank.add_user(teller)
    teller.create_account(customer, False)
    teller_created_account = bank.get_account_by_id(4)

    assert teller_created_account.get_account_type() == "savings"
    assert teller_created_account.get_balance() == 0.00

    # Admins should be able to see suspicious activity and freeze accounts
    admin = Admin("root", 4, "root", bank)
    bank.add_user(admin)

    account.deposit(10000.00)
    assert account.get_balance() == 10350.00
    admin.toggle_frozen(account)

    with pytest.raises(AccountFrozenException):
        account.withdraw(100.00)
    assert account.get_balance() == 10350.00