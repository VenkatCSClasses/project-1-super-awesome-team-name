import sys
sys.path.append('./server/src')

from teller import Teller
from customer import Customer
from bank import Bank

class TestTeller:
    
    def test_get_name(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Teller("john", 5, "password", bank)
        assert test.get_name() == "john"
    
    def test_get_id(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Teller("john", 5, "password", bank)
        assert test.get_id() == 5

    def test_get_password(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Teller("john", 5, "password", bank)
        assert test.get_passwd() == "password"

    def test_get_permissions(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Teller("john", 5, "password", bank)
        assert test.get_permissions() == 1

    def test_get_user_acc_details(self):
        """integration test: tests proper input for constructor"""
        bank = Bank()
        test = Teller("john", 5, "password", bank)
        assert test.get_user_acc_details() == ('Name:', 'john' , '\nID:', 5 , '\naccType: Teller')

    def test_create_close_account(self):
        """integration test: ensures closed accounts are no longer accessible"""
        bank = Bank()
        test = Teller("john", 5, "password", bank)
        test2 = Customer("james", 7, "pass", bank)
        test.create_account(test2, True)
        assert len(test2.get_accounts()) == 1

        acc = test2.get_accounts().get(1)
        
        test.close_account(test2, acc)
        assert len(test2.get_accounts()) == 0

    def test_get_accounts(self):
        """integration test: ensures accounts are properly added to a customer"""
        bank = Bank()
        teller = Teller("john", 5, "password", bank)
        customer = Customer("james", 7, "pass", bank)
        teller.create_account(customer, True)
        teller.create_account(customer, True)
        assert len(customer.get_accounts()) == 2
