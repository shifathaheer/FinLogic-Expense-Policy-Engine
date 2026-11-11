
import unittest
from decimal import Decimal

from common.models import ExpenseLine
from module_a_validation.currency_converter import convert_to_inr


class TestCurrencyConverter(unittest.TestCase):

    def test_inr_expense(self):
        expense = ExpenseLine(
            line_id="C001",
            category="HOTEL",
            expense_date="2026-11-08",
            amount=Decimal("2500"),
            currency="INR"
        )

        result = convert_to_inr(expense)

        self.assertEqual(result, Decimal("2500.00"))
        self.assertEqual(expense.applied_rate, Decimal("1"))

    def test_card_rate_conversion(self):
        expense = ExpenseLine(
            line_id="C002",
            category="HOTEL",
            expense_date="2026-11-08",
            amount=Decimal("100"),
            currency="USD",
            card_rate=Decimal("85")
        )

        result = convert_to_inr(expense)

        self.assertEqual(result, Decimal("8500.00"))

    def test_policy_rate_conversion(self):
        expense = ExpenseLine(
            line_id="C003",
            category="HOTEL",
            expense_date="2026-11-08",
            amount=Decimal("100"),
            currency="USD",
            policy_rate=Decimal("84")
        )

        result = convert_to_inr(expense)

        self.assertEqual(result, Decimal("8400.00"))

    def test_missing_exchange_rate(self):
        expense = ExpenseLine(
            line_id="C004",
            category="HOTEL",
            expense_date="2026-11-08",
            amount=Decimal("100"),
            currency="USD"
        )

        with self.assertRaises(ValueError):
            convert_to_inr(expense)


if __name__ == "__main__":
    unittest.main()
