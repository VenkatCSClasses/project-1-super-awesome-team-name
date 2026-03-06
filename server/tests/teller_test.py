import sys
sys.path.append('./server/src')

from teller import Teller
from customer import Customer

class TestTeller:
    
    def test_get_name(self):
        test = Teller("john", 5, "password")
        assert test.get_name() == "john"
    
    def test_get_id(self):
        test = Teller("john", 5, "password")
        assert test.get_id() == 5

    def test_get_password(self):
        test = Teller("john", 5, "password")
        assert test.get_passwd() == "password"

    def test_get_acc_type(self):
        test = Teller("john", 5, "password")
        assert test.get_accType() == 1

    def test_get_user_acc_details(self):
        test = Teller("john", 5, "password")
        assert test.get_user_acc_details() == ('Name:', 'john' , '\nID:', 5 , '\naccType: Teller')

    def test_create_close_account(self):
        test = Teller("john", 5, "password")
        test2 = Customer("james", 7, "pass")
        acc = test.create_account(test2, True)
        assert test2.get_accounts().len() != 0

        test.close_account(test2,acc)
        assert test2.get_accounts().len() == 0
