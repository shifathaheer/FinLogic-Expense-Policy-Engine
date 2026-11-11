
import unittest
from decimal import Decimal

from common.models import ExpenseLine
from module_a_validation.claim_processor import process_claim


class TestModuleA(unittest.TestCase):

    def test_valid_expense(self):
        expense = ExpenseLine(
            line_id="EXP001",
            category="TRAVEL",
            expense_date="2026-11-08",
            amount=Decimal("1000"),
            currency="INR",
            receipt=True
        )

        result = process_claim(expense)
        self.assertEqual(result["status"], "VALID")

    def test_invalid_expense(self):
        expense = ExpenseLine(
            line_id="EXP002",
            category="INVALID",
            expense_date="2026-11-08",
            amount=Decimal("500"),
            currency="INR",
            receipt=True
        )

        result = process_claim(expense)
        self.assertEqual(result["status"], "REJECTED")

    def test_process_valid_meal_claim(self):
        expense = ExpenseLine(
            line_id="EXP003",
            category="MEAL",
            expense_date="2026-11-08",
            amount=Decimal("400"),
            currency="INR",
            receipt=True
        )

        result = process_claim(expense)

        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["eligible_amount"], Decimal("400"))

    def test_rejected_meal_claim(self):
        expense = ExpenseLine(
            line_id="EXP004",
            category="MEAL",
            expense_date="2026-11-08",
            amount=Decimal("999999"),
            currency="INR",
            receipt=True
        )

        result = process_claim(expense)

        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["eligible_amount"], Decimal("0.00"))
        self.assertTrue(len(result["errors"]) > 0)

    def test_duplicate_expense_rejected(self):
        existing_expense = ExpenseLine(
            line_id="EXP005",
            category="TRAVEL",
            expense_date="2026-11-08",
            amount=Decimal("1000"),
            currency="INR",
            receipt=True,
            vendor="ABC Travels"
        )

        new_expense = ExpenseLine(
            line_id="EXP006",
            category="TRAVEL",
            expense_date="2026-11-08",
            amount=Decimal("1000"),
            currency="INR",
            receipt=True,
            vendor="ABC Travels"
        )

        result = process_claim(
            new_expense,
            existing_expenses=[existing_expense]
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertIn("DUPLICATE_EXPENSE", result["errors"])
        self.assertEqual(result["eligible_amount"], Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
