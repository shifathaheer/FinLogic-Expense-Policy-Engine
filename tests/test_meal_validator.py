
import unittest
from module_a_validation.meal_validator import validate_meal_expense


class TestMealValidator(unittest.TestCase):

    def test_valid_meal(self):
        result = validate_meal_expense(400, 500)
        self.assertEqual(result, [])

    def test_exceeded_meal_limit(self):
        result = validate_meal_expense(600, 500)
        self.assertIn(
            "Meal expense exceeds the permitted limit",
            result
        )

    def test_invalid_meal_amount(self):
        result = validate_meal_expense(-100, 500)
        self.assertIn("Invalid meal expense amount", result)


if __name__ == "__main__":
    unittest.main()
