from common.models import ExpenseLine
from common.rule_ids import INVALID_EMPLOYEE


def validate_employee(expense: ExpenseLine):
    errors = []

    if not expense.employee_id:
        errors.append(INVALID_EMPLOYEE)

    if not expense.employee_name:
        errors.append(INVALID_EMPLOYEE)

    return errors