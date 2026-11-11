import unittest
from decimal import Decimal

from common.models import ExpenseLine
from module_a_validation.duplicate_detector import detect_duplicate


class TestDuplicateDetector(unittest.TestCase):

    def test_duplicate_expense(self):
        expense1 = ExpenseLine(
            line_id="L001",
            category="HOTEL",
            expense_date="2026-11-08",
            amount=Decimal("2500"),
            currency="INR",
            vendor="ABC Hotel"
        )

        expense2 = ExpenseLine(
            line_id="L002",
            category="HOTEL",
            expense_date="2026-11-08",
            amount=Decimal("2500"),
            currency="INR",
            vendor="ABC Hotel"
        )

        self.assertTrue(detect_duplicate(expense1, [expense2]))

    def test_non_duplicate_expense(self):
        expense1 = ExpenseLine(
            line_id="L001",
            category="HOTEL",
            expense_date="2026-11-08",
            amount=Decimal("2500"),
            currency="INR",
            vendor="ABC Hotel"
        )

        expense2 = ExpenseLine(
            line_id="L002",
            category="HOTEL",
            expense_date="2026-11-09",
            amount=Decimal("3000"),
            currency="INR",
            vendor="XYZ Hotel"
        )

        self.assertFalse(detect_duplicate(expense1, [expense2]))


if __name__ == "__main__":
    unittest.main()