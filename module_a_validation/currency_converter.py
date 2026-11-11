
from decimal import Decimal, ROUND_HALF_UP


def convert_to_inr(expense):
    """
    Convert an expense amount into INR.

    Rate selection:
    1. Use card_rate if available.
    2. Otherwise, use policy_rate.
    3. INR expenses use a rate of 1.
    """

    currency = expense.currency.upper()

    # INR does not require conversion
    if currency == "INR":
        expense.applied_rate = Decimal("1")
        return expense.amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    # Select the exchange rate
    if expense.card_rate is not None:
        rate = Decimal(str(expense.card_rate))

    elif expense.policy_rate is not None:
        rate = Decimal(str(expense.policy_rate))

    else:
        raise ValueError("Exchange rate not available")

    # Validate exchange rate
    if rate <= 0:
        raise ValueError("Exchange rate must be greater than zero")

    # Save the applied rate
    expense.applied_rate = rate

    # Convert amount into INR
    converted_amount = expense.amount * rate

    return converted_amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
