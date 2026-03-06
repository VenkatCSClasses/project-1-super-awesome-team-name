import sys
sys.path.append('./server/src')

from server.src.transaction import Transaction
from datetime import datetime, timezone


class TestTransaction:

    def test_constructor_getters(self):
        """Test the constructor and getters of the transaction class."""
        # Test 1: Positive amount
        trans1 = Transaction(0, 0, 1, 50)
        assert trans1.get_absolute_id() == 0
        assert trans1.get_relative_id() == 0
        assert trans1.get_account_num() == 1
        assert trans1.get_amount() == 50
        assert trans1.get_time().date() == datetime.now(timezone.utc).date()

        # Test 2: Negative amount
        trans2 = Transaction(1, 1, 1, -50)
        assert trans2.get_absolute_id() == 1
        assert trans2.get_relative_id() == 1
        assert trans2.get_account_num() == 1
        assert trans2.get_amount() == -50
        assert trans2.get_time().date() == datetime.now(timezone.utc).date()

        # Test 3: Zero amount (Boundary case)
        trans3 = Transaction(2, 0, 2, 0.01)
        assert trans3.get_absolute_id() == 2
        assert trans3.get_relative_id() == 0
        assert trans3.get_account_num() == 2
        assert trans3.get_amount() == 0.01
        assert trans3.get_time().date() == datetime.now(timezone.utc).date()

        # Test 4: Large values (Boundary case)
        trans4 = Transaction(999999, 500, 100, 1000000.00)
        assert trans4.get_absolute_id() == 999999
        assert trans4.get_relative_id() == 500
        assert trans4.get_account_num() == 100
        assert trans4.get_amount() == 1000000.00
        assert trans4.get_time().date() == datetime.now(timezone.utc).date()

    def test_str(self):
        """Test the human-readable string return."""
        abs_id = 5
        rel_id = 2
        acc_num = 123
        amount = 75.0
        
        trans = Transaction(abs_id, rel_id, acc_num, amount)
        
        # Get the timestamp from the object since it is set on init
        timestamp = trans.get_time().strftime("%A, %B %d, %Y, %H:%M")
        
        expected_str = f"Transaction (Absolute ID: {abs_id}, Relative ID: {rel_id}) of account {acc_num} occured on {timestamp} with the amount changed being {amount}."
        
        assert str(trans) == expected_str
