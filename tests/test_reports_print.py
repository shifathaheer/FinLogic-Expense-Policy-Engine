
from module_b_approval.reports import print_monthly_cost_centre_report


def test_print_monthly_report(capsys):
    report = {
        "CC101": {
            "claim_count": 2,
            "total_claimed": 15000,
            "approved_amount": 14000,
            "taxable_amount": 1000,
            "total_payout": 12000,
            "total_recovery": 0,
            "claim_ids": ["CLM001", "CLM002"],
        }
    }

    print_monthly_cost_centre_report(report, 2026, 11)

    output = capsys.readouterr().out

    assert "CC101" in output
    assert "Claim Count" in output
    assert "Total Payout" in output
    assert "CLM001" in output


def test_print_empty_monthly_report(capsys):
    print_monthly_cost_centre_report({}, 2026, 11)

    output = capsys.readouterr().out

    assert "No settled claims found" in output
