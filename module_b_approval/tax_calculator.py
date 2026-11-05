
from decimal import Decimal

from common.models import ApprovalDecision


DOMESTIC_PER_DIEM_TAX_FREE_LIMIT = Decimal("1000")


def calculate_taxable_amount(
    line_decisions,
    domestic_per_diem_limit=DOMESTIC_PER_DIEM_TAX_FREE_LIMIT,
):
    """
    Calculate the total taxable reimbursement amount.

    Rules:
    1. E5-approved exception amounts are taxable.
    2. Rejected and returned lines are not taxable.
    3. Domestic per diem above Rs. 1000 per day is taxable.
    4. International per diem is not subject to the domestic limit.
    """

    taxable_total = Decimal("0")
    domestic_per_diem_by_day = {}

    for line in line_decisions:

        category = line.category.upper()

        amount = Decimal(str(line.amount))
        exception_amount = Decimal(str(line.exception_amount))

        decision = getattr(line, "decision", None)

        if isinstance(decision, str):
            try:
                decision = ApprovalDecision(decision.upper())
            except ValueError:
                pass

        # Rejected and returned lines are not taxable.
        if decision in (
            ApprovalDecision.REJECT,
            ApprovalDecision.RETURN,
        ):
            continue

        # Only E5-approved exceptions are taxable.
        exception_approved = getattr(line, "exception_approved", None)

        if exception_approved is True:
            taxable_total += exception_amount

        # Preserve compatibility with older expense-line objects.
        elif not hasattr(line, "exception_approved"):
            taxable_total += exception_amount

        # Group domestic per diem by expense date.
        if category == "PER_DIEM":

            travel_type = getattr(line, "travel_type", None)

            if travel_type is None:
                travel_type = "DOMESTIC"

            if travel_type.upper() == "DOMESTIC":

                expense_date = getattr(line, "expense_date", None)

                if expense_date is None:
                    expense_date = "UNKNOWN"

                if expense_date not in domestic_per_diem_by_day:
                    domestic_per_diem_by_day[expense_date] = Decimal("0")

                domestic_per_diem_by_day[expense_date] += amount

    # Calculate tax only after adding all per diem lines for each day.
    for daily_amount in domestic_per_diem_by_day.values():

        taxable_total += max(
            Decimal("0"),
            daily_amount - domestic_per_diem_limit,
        )

    return taxable_total
