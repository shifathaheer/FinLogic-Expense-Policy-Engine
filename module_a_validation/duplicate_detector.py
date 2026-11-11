def detect_duplicate(expense, existing_expenses):

    for existing in existing_expenses:

        if (
            expense.amount == existing.amount
            and expense.expense_date == existing.expense_date
            and expense.category.strip().upper()
                == existing.category.strip().upper()
            and expense.currency == existing.currency
            and expense.vendor == existing.vendor
        ):
            return True

    return False