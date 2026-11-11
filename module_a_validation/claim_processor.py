
from decimal import Decimal

from module_a_validation.policy_loader import load_policy
from module_a_validation.hotel_validator import validate_hotel_expense
from module_a_validation.per_diem_validator import validate_per_diem
from module_a_validation.travel_validator import validate_travel_expense
from module_a_validation.meal_validator import validate_meal_expense
from module_a_validation.receipt_validator import validate_receipt
from module_a_validation.validation_engine import validate_expense
from module_a_validation.duplicate_detector import detect_duplicate
from module_a_validation.currency_converter import convert_to_inr

from common.models import ExpenseLine


def process_claim(expense: ExpenseLine, travel_days=1, existing_expenses=None):

    errors = []

    # Load company policy
    policy = load_policy()

    # Check for duplicate expenses
    if existing_expenses is None:
        existing_expenses = []

    if detect_duplicate(expense, existing_expenses):
        errors.append("DUPLICATE_EXPENSE")

    # General validation
    errors.extend(validate_expense(expense))

    # Convert expense amount into INR
    validation_amount = expense.amount

    if not any("INVALID" in str(error) for error in errors):
        try:
            validation_amount = convert_to_inr(expense)
        except ValueError:
            errors.append("INVALID_CURRENCY_RATE")

    # Category-based validation
    category = expense.category.strip().lower()

    if category == "hotel":
        errors.extend(
            validate_hotel_expense(
                validation_amount,
                Decimal(str(policy["hotel_limit"]))
            )
        )

    elif category == "meal":
        errors.extend(
            validate_meal_expense(
                validation_amount,
                Decimal(str(policy["meal_limit"]))
            )
        )

    elif category == "travel":
        errors.extend(
            validate_travel_expense(
                validation_amount,
                Decimal(str(policy["travel_limit"]))
            )
        )

    elif category == "per_diem":
        errors.extend(
            validate_per_diem(
                validation_amount,
                Decimal(str(policy["per_diem_daily_limit"])),
                travel_days
            )
        )

    # Receipt validation
    errors.extend(
        validate_receipt(
            validation_amount,
            expense.receipt,
            Decimal(str(policy["receipt_required_above"]))
        )
    )

    # Update validation results
    if errors:
        expense.validation_status = "REJECTED"
        expense.eligible_amount = Decimal("0.00")
        expense.rejected_amount = validation_amount
        expense.rule_ids.extend(errors)

    else:
        expense.validation_status = "VALID"
        expense.eligible_amount = validation_amount
        expense.rejected_amount = Decimal("0.00")

    # Store converted amount for reference
    expense.details["converted_amount_inr"] = validation_amount

    return {
        "status": expense.validation_status,
        "errors": errors,
        "eligible_amount": expense.eligible_amount,
        "rejected_amount": expense.rejected_amount
    }
