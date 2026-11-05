
from datetime import date
from decimal import Decimal

from common.models import (
    Employee,
    ValidatedClaim,
    ClaimWorkflow,
    SettlementResult,
)
from module_b_approval.reports import (
    generate_monthly_cost_centre_report,
)


def test_monthly_cost_centre_report():
    employee = Employee(
        employee_id="E101",
        name="Test Employee",
        grade="E3",
        cost_centre="CC01",
        manager_id="M01",
        base_city="Bengaluru",
    )

    claim = ValidatedClaim(
        claim_id="CL001",
        employee_id="E101",
        total_claimed=Decimal("12000"),
        eligible_amount=Decimal("10000"),
        exception_amount=Decimal("2000"),
        rejected_amount=Decimal("0"),
    )

    workflow = ClaimWorkflow(claim=claim)

    settlement = SettlementResult(
        claim_id="CL001",
        approved_amount=Decimal("10000"),
        taxable_amount=Decimal("2000"),
        advance_amount=Decimal("3000"),
        payout_amount=Decimal("7000"),
        recovery_amount=Decimal("0"),
        settlement_date=date(2026, 11, 4),
    )

    report = generate_monthly_cost_centre_report(
        workflows=[workflow],
        employees={"E101": employee},
        settlements={"CL001": settlement},
        year=2026,
        month=11,
    )

    assert report["CC01"]["claim_count"] == 1
    assert report["CC01"]["total_claimed"] == Decimal("12000")
    assert report["CC01"]["approved_amount"] == Decimal("10000")
    assert report["CC01"]["taxable_amount"] == Decimal("2000")
    assert report["CC01"]["total_payout"] == Decimal("7000")
    assert report["CC01"]["total_recovery"] == Decimal("0")


def test_report_excludes_other_months():
    report = generate_monthly_cost_centre_report(
        workflows=[],
        employees={},
        settlements={},
        year=2026,
        month=11,
    )

    assert report == {}
