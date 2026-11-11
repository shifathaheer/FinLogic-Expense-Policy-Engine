def validate_travel_expense(amount, travel_limit):
    errors = []

    if amount <= 0:
        errors.append("Invalid travel expense amount")

    elif amount > travel_limit:
        errors.append("Travel expense exceeds the permitted limit")

    return errors