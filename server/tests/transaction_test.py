import sys
sys.path.append('./server/src')

from transaction import Transaction
from datetime import datetime, timezone


class TestTransaction:

    def test_constructor_getters(self):
        """Test the constructor and getters of the transaction class."""
        # Test 1: Positive amount
        trans1 = Transaction(0, 0, 1, 50, 50)
        assert trans1.get_absolute_id() == 0
        assert trans1.get_relative_id() == 0
        assert trans1.get_account_id() == 1
        assert trans1.get_amount() == 50
        assert trans1.get_post_balance() == 50
        assert trans1.get_time().date() == datetime.now(timezone.utc).date()

        # Test 2: Negative amount
        trans2 = Transaction(1, 1, 1, -50, 0)
        assert trans2.get_absolute_id() == 1
        assert trans2.get_relative_id() == 1
        assert trans2.get_account_id() == 1
        assert trans2.get_amount() == -50
        assert trans2.get_post_balance() == 0
        assert trans2.get_time().date() == datetime.now(timezone.utc).date()

        # Test 3: Zero amount (Boundary case)
        trans3 = Transaction(2, 0, 2, 0.01, 2.01)
        assert trans3.get_absolute_id() == 2
        assert trans3.get_relative_id() == 0
        assert trans3.get_account_id() == 2
        assert trans3.get_amount() == 0.01
        assert trans3.get_post_balance() == 2.01
        assert trans3.get_time().date() == datetime.now(timezone.utc).date()

        # Test 4: Large values (Boundary case)
        trans4 = Transaction(999999, 500, 100, 1000000.00, 1000000.01)
        assert trans4.get_absolute_id() == 999999
        assert trans4.get_relative_id() == 500
        assert trans4.get_account_id() == 100
        assert trans4.get_amount() == 1000000.00
        assert trans4.get_post_balance() == 1000000.01
        assert trans4.get_time().date() == datetime.now(timezone.utc).date()
