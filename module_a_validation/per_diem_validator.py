def validate_per_diem(amount, daily_limit, number_of_days):
    errors = []

    if amount <= 0:
        errors.append("Invalid per diem amount")

    elif number_of_days <= 0:
        errors.append("Invalid number of travel days")

    else:
        total_limit = daily_limit * number_of_days

        if amount > total_limit:
            errors.append("Per diem exceeds the allowed limit")

    return errors