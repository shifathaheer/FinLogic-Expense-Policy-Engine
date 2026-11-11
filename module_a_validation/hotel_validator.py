def validate_hotel_expense(amount, hotel_limit):
    errors = []

    if amount <= 0:
        errors.append("Invalid hotel expense amount")

    elif amount > hotel_limit:
        errors.append("Hotel expense exceeds the permitted limit")

    return errors