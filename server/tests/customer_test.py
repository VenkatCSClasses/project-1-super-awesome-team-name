import pytest
from .customer import Customer

class TestCustomer:
    def test_get_name(self):
        test = Customer("john", 5, "password")
        assert test.name == "john"
    
    def test_get_id(self):
        test = Customer("john", 5, "password")
        assert test.id == 5

    def test_get_password(self):
        test = Customer("john", 5, "password")
        assert test.password == "password"

    def test_get_acc_type(self):
        test = Customer("john", 5, "password")
        assert test.accType == 0

    def test_get_acc_details(self):
        test = Customer("john", 5, "password")
        assert test.get_acc_details() == "Name: john\nID: 5\naccType: Customer"