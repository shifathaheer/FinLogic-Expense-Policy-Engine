
from collections import defaultdict
from decimal import Decimal


def generate_monthly_cost_centre_report(
    workflows,
    employees,
    settlements,
    year,
    month,
):
    """
    workflows: list of ClaimWorkflow objects
    employees: dictionary of employee_id -> Employee
    settlements: dictionary of claim_id -> SettlementResult
    """

    report = defaultdict(
        lambda: {
            "claim_count": 0,
            "total_claimed": Decimal("0"),
            "approved_amount": Decimal("0"),
            "taxable_amount": Decimal("0"),
            "total_payout": Decimal("0"),
            "total_recovery": Decimal("0"),
            "claim_ids": [],
        }
    )

    for workflow in workflows:
        claim = workflow.claim
        settlement = settlements.get(claim.claim_id)

        # Ignore claims that have not been settled.
        if settlement is None or settlement.settlement_date is None:
            continue

        # Include only settlements from the requested month.
        if (
            settlement.settlement_date.year != year
            or settlement.settlement_date.month != month
        ):
            continue

        employee = employees.get(claim.employee_id)

        if employee is None:
            raise ValueError(
                f"Employee {claim.employee_id} not found"
            )

        cost_centre = employee.cost_centre
        row = report[cost_centre]

        row["claim_count"] += 1
        row["total_claimed"] += claim.total_claimed
        row["approved_amount"] += settlement.approved_amount
        row["taxable_amount"] += settlement.taxable_amount
        row["total_payout"] += settlement.payout_amount
        row["total_recovery"] += settlement.recovery_amount
        row["claim_ids"].append(claim.claim_id)

    return dict(report)

def print_monthly_cost_centre_report(report, year, month):
    print("\n========== MONTHLY COST CENTRE REPORT ==========")
    print(f"Month: {month:02d}/{year}")
    print("------------------------------------------------")

    if not report:
        print("No settled claims found for this month.")
        return

    for cost_centre, data in sorted(report.items()):
        print(f"\nCost Centre: {cost_centre}")
        print(f"Claim Count     : {data['claim_count']}")
        print(f"Total Claimed   : Rs. {data['total_claimed']}")
        print(f"Approved Amount : Rs. {data['approved_amount']}")
        print(f"Taxable Amount  : Rs. {data['taxable_amount']}")
        print(f"Total Payout    : Rs. {data['total_payout']}")
        print(f"Total Recovery  : Rs. {data['total_recovery']}")
        print(f"Claim IDs       : {', '.join(data['claim_ids'])}")

    print("\n================================================")
