from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from module_b_approval.tax_calculator import calculate_taxable_amount

from module_b_approval.settlement import (
    calculate_settlement,
    calculate_settlement_deadline,
)


# 1. E5-approved exception amount is taxable.
def test_exception_amount_is_taxable():

    lines = [
        SimpleNamespace(
            category="HOTEL",
            amount=Decimal("5000"),
            exception_amount=Decimal("1000"),
            exception_approved=True,
            decision="APPROVE",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("1000")


# 2. Exception not approved by E5 is not taxable.
def test_unapproved_exception_is_not_taxable():

    lines = [
        SimpleNamespace(
            category="HOTEL",
            amount=Decimal("5000"),
            exception_amount=Decimal("1000"),
            exception_approved=False,
            decision="APPROVE",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("0")


# 3. Pending exception approval is not taxable.
def test_pending_exception_is_not_taxable():

    lines = [
        SimpleNamespace(
            category="HOTEL",
            amount=Decimal("5000"),
            exception_amount=Decimal("1000"),
            exception_approved=None,
            decision="APPROVE",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("0")


# 4. Domestic per diem above Rs. 1000 is taxable.
def test_domestic_per_diem_above_limit_is_taxable():

    lines = [
        SimpleNamespace(
            category="PER_DIEM",
            amount=Decimal("1500"),
            exception_amount=Decimal("0"),
            travel_type="DOMESTIC",
            decision="APPROVE",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("500")


# 5. Domestic per diem within Rs. 1000 is not taxable.
def test_per_diem_within_limit_is_not_taxable():

    lines = [
        SimpleNamespace(
            category="PER_DIEM",
            amount=Decimal("800"),
            exception_amount=Decimal("0"),
            travel_type="DOMESTIC",
            decision="APPROVE",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("0")


# 6. International per diem is not subject to domestic Rs. 1000 limit.
def test_international_per_diem_is_not_taxable_under_domestic_limit():

    lines = [
        SimpleNamespace(
            category="PER_DIEM",
            amount=Decimal("1500"),
            exception_amount=Decimal("0"),
            travel_type="INTERNATIONAL",
            decision="APPROVE",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("0")


# 7. Rejected exception amount should not be taxable.
def test_rejected_exception_is_not_taxable():

    lines = [
        SimpleNamespace(
            category="HOTEL",
            amount=Decimal("5000"),
            exception_amount=Decimal("1000"),
            exception_approved=True,
            decision="REJECT",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("0")


# 8. Returned exception amount should not be taxable.
def test_returned_exception_is_not_taxable():

    lines = [
        SimpleNamespace(
            category="HOTEL",
            amount=Decimal("5000"),
            exception_amount=Decimal("1000"),
            exception_approved=True,
            decision="RETURN",
        )
    ]

    assert calculate_taxable_amount(lines) == Decimal("0")


# 9. Advance is deducted from approved claim.
def test_advance_is_deducted_from_claim():

    result = calculate_settlement(
        "CL001",
        Decimal("10000"),
        Decimal("500"),
        Decimal("3000"),
    )

    assert result.payout_amount == Decimal("7000")
    assert result.recovery_amount == Decimal("0")


# 10. Advance larger than approved claim.
def test_advance_larger_than_approved_claim():

    result = calculate_settlement(
        "CL002",
        Decimal("5000"),
        Decimal("0"),
        Decimal("7000"),
    )

    assert result.payout_amount == Decimal("0")
    assert result.recovery_amount == Decimal("2000")


# 11. Settlement deadline is five working days.
def test_settlement_deadline_is_five_working_days():

    start = datetime(2026, 11, 2, 10, 0)

    deadline = calculate_settlement_deadline(
        start,
        set(),
        set(),
    )

    assert deadline == datetime(2026, 11, 9, 10, 0)


# 12. Negative settlement amounts are not allowed.
def test_negative_settlement_amount_is_rejected():

    import pytest

    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_settlement(
            "CL003",
            Decimal("-100"),
            Decimal("0"),
            Decimal("0"),
        )