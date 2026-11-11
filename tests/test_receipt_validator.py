
import unittest
from decimal import Decimal

from module_a_validation.receipt_validator import validate_receipt


class TestReceiptValidator(unittest.TestCase):

    def test_receipt_not_required(self):
        result = validate_receipt(
            Decimal("400"), False, Decimal("500")
        )
        self.assertEqual(result, [])

    def test_missing_receipt(self):
        result = validate_receipt(
            Decimal("700"), False, Decimal("500")
        )
        self.assertIn("MISSING_RECEIPT", result)

    def test_receipt_provided(self):
        result = validate_receipt(
            Decimal("700"), True, Decimal("500")
        )
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
