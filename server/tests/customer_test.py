import sys
sys.path.append('./server/src')

from customer import Customer
from checking_account import CheckingAccount
from bank import Bank

class TestCustomer:
    
    def test_get_name(self):
        bank = Bank()
        test = Customer("john", 5, "password", bank)
        assert test.get_name() == "john"
    
    def test_get_id(self):
        bank = Bank()
        test = Customer("john", 5, "password", bank)
        assert test.get_id() == 5

    def test_get_password(self):
        bank = Bank()
        test = Customer("john", 5, "password", bank)
        assert test.get_passwd() == "password"

    def test_get_acc_type(self):
        bank = Bank()
        test = Customer("john", 5, "password", bank)
        assert test.get_permissions() == 0

    def test_get_user_acc_details(self):
        bank = Bank()
        test = Customer("john", 5, "password", bank)
        assert test.get_user_acc_details() == ('Name:', 'john' , '\nID:', 5 , '\naccType: Customer')

    def test_get_total_transact_hist(self):
        bank = Bank()
        test = Customer("john", 5, "password", bank)
        assert test.get_total_transact_hist() == ""

        acc1 = CheckingAccount(1, bank, 500.00)
        acc2 = CheckingAccount(2, bank, 500.00)
        test.get_accounts().append(acc1)
        print("hello")
        test.get_accounts().append(acc2)
  
        acc1.deposit(50)
        acc1.withdraw(20)
        
        assert test.get_total_transact_hist() == acc1.get_all_transaction_str()
        
        acc2.deposit(2)
        acc2.withdraw(50)
        assert test.get_total_transact_hist() == acc1.get_all_transaction_str() , acc2.get_all_transaction_str()