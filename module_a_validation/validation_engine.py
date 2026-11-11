
from datetime import datetime
from decimal import Decimal
from common.models import ExpenseLine
from common import rule_ids


VALID_CATEGORIES = {
    "HOTEL",
    "MEAL",
    "TRAVEL",
    "PER_DIEM"
}


def validate_expense(expense: ExpenseLine):
    errors = []

    # Check expense ID
    if not expense.line_id:
        errors.append(rule_ids.INVALID_EMPLOYEE)

    # Check expense category
    if not expense.category or expense.category.strip().upper() not in VALID_CATEGORIES:
        errors.append(rule_ids.INVALID_EXPENSE_TYPE)

    # Check amount
    if expense.amount <= Decimal("0"):
        errors.append(rule_ids.INVALID_AMOUNT)

    # Check currency
    if not expense.currency:
        errors.append("INVALID_CURRENCY")

    # Check expense date
    try:
        datetime.strptime(expense.expense_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        errors.append(rule_ids.INVALID_EXPENSE_DATE)

    return errors
