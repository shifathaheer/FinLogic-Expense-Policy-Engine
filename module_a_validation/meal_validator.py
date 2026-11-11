def validate_meal_expense(amount, meal_limit):
    errors = []

    if amount <= 0:
        errors.append("Invalid meal expense amount")

    elif amount > meal_limit:
        errors.append("Meal expense exceeds the permitted limit")

    return errors