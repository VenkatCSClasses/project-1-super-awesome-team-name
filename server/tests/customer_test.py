import sys
sys.path.append('./server/src')

from customer import Customer
from checking_account import CheckingAccount
from bank import Bank

class TestCustomer:
    
    def test_get_name(self):
        test = Customer("john", 5, "password")
        assert test.get_name() == "john"
    
    def test_get_id(self):
        test = Customer("john", 5, "password")
        assert test.get_id() == 5

    def test_get_password(self):
        test = Customer("john", 5, "password")
        assert test.get_passwd() == "password"

    def test_get_acc_type(self):
        test = Customer("john", 5, "password")
        assert test.get_permissions() == 0

    def test_get_user_acc_details(self):
        test = Customer("john", 5, "password")
        assert test.get_user_acc_details() == ('Name:', 'john' , '\nID:', 5 , '\naccType: Customer')

    def test_get_total_transact_hist(self):
        bank = Bank()
        test = Customer("john", 5, "password", bank)
        assert test.get_total_transact_hist() == ""

        acc1 = CheckingAccount(1, bank, 500.00)
        acc2 = CheckingAccount(2, bank, 500.00)
        test.register_account(acc1)
        test.register_account(acc2)
  
        acc1.deposit(50)
        acc1.withdraw(20)
        
        print("Hello")
        assert test.get_total_transact_hist() == acc1.get_all_transaction_str()
        
        acc2.deposit(2)
        acc2.withdraw(50)
        assert test.get_total_transact_hist() == acc1.get_all_transaction_str() , acc2.get_all_transaction_str()