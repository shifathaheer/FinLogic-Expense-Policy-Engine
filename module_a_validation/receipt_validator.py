
def validate_receipt(amount, receipt, receipt_required_above):
    errors = []

    if amount > receipt_required_above and not receipt:
        errors.append("MISSING_RECEIPT")

    return errors
