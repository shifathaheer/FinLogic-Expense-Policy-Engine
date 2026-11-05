
from datetime import datetime
from decimal import Decimal

import pytest

from common.models import (
    Employee,
    ValidatedClaim,
    ExpenseLineResult,
    ClaimWorkflow,
    ApprovalStep,
    ApprovalDecision,
    ClaimStatus,
)

from module_b_approval.escalation_manager import escalate_claim


def create_workflow(approver_id="M01", deadline=None, lines=None):
    claim = ValidatedClaim(
        claim_id="CL001",
        employee_id="E01",
        total_claimed=Decimal("5000"),
        eligible_amount=Decimal("5000"),
        exception_amount=Decimal("0"),
        rejected_amount=Decimal("0"),
        line_decisions=lines or [],
    )

    step = ApprovalStep(
        approver_id=approver_id,
        approver_role="MANAGER",
        sequence=1,
        status=ApprovalDecision.PENDING,
        deadline=deadline or datetime(2026, 1, 5, 9, 0),
    )

    return ClaimWorkflow(
        claim=claim,
        approval_chain=[step],
        status=ClaimStatus.PENDING_APPROVAL,
    )


def test_escalation_after_sla_breach():
    workflow = create_workflow()

    employees = {
        "M01": Employee("M01", "Manager", "E4", "CC01", "H01", "Bengaluru"),
        "H01": Employee("H01", "Head", "E5", "CC01", None, "Bengaluru"),
    }

    result = escalate_claim(
        workflow,
        employees,
        datetime(2026, 1, 6, 10, 0),
        set(),
        set(),
    )

    assert result.current_step == 1
    assert result.approval_chain[1].approver_id == "H01"
    assert result.approval_chain[1].approver_role == "ESCALATED_MANAGER"
    assert result.approval_chain[0].status == ApprovalDecision.ESCALATED


def test_escalation_before_deadline():
    workflow = create_workflow()

    employees = {
        "M01": Employee("M01", "Manager", "E4", "CC01", "H01", "Bengaluru"),
        "H01": Employee("H01", "Head", "E5", "CC01", None, "Bengaluru"),
    }

    with pytest.raises(ValueError, match="deadline has not been breached"):
        escalate_claim(
            workflow,
            employees,
            datetime(2026, 1, 5, 8, 0),
            set(),
            set(),
        )


def test_current_approver_not_found():
    workflow = create_workflow()

    with pytest.raises(ValueError, match="Current approver not found"):
        escalate_claim(
            workflow,
            {},
            datetime(2026, 1, 6, 10, 0),
            set(),
            set(),
        )


def test_first_top_level_breach_resets_deadline():
    workflow = create_workflow()

    employees = {
        "M01": Employee("M01", "Top Manager", "E5", "CC01", None, "Bengaluru"),
    }

    result = escalate_claim(
        workflow,
        employees,
        datetime(2026, 1, 6, 10, 0),
        set(),
        set(),
    )

    assert result.consecutive_top_escalations == 1
    assert result.status == ClaimStatus.PENDING_APPROVAL
    assert result.approval_chain[0].deadline == datetime(2026, 1, 9, 10, 0)
    assert result.audit_history[-1].action == "TOP_LEVEL_ESCALATION_RETRY"


def test_second_top_level_breach_splits_expense_lines():
    lines = [
        ExpenseLineResult(
            line_id="L01",
            category="TRAVEL",
            amount=Decimal("3000"),
            eligible_amount=Decimal("3000"),
        ),
        ExpenseLineResult(
            line_id="L02",
            category="HOTEL",
            amount=Decimal("2000"),
            eligible_amount=Decimal("1500"),
            exception_amount=Decimal("500"),
            has_exception=True,
        ),
    ]

    workflow = create_workflow(lines=lines)

    employees = {
        "M01": Employee("M01", "Top Manager", "E5", "CC01", None, "Bengaluru"),
    }

    # First top-level breach
    escalate_claim(
        workflow,
        employees,
        datetime(2026, 1, 6, 10, 0),
        set(),
        set(),
    )

    # Second breach, after the reset deadline
    result = escalate_claim(
        workflow,
        employees,
        datetime(2026, 1, 12, 10, 0),
        set(),
        set(),
    )

    assert result.consecutive_top_escalations == 2
    assert result.status == ClaimStatus.RETURNED

    assert result.claim.line_decisions[0].decision == ApprovalDecision.AUTO_APPROVED
    assert result.claim.line_decisions[1].decision == ApprovalDecision.RETURN

    assert result.audit_history[-1].action == "RETURNED_EXCEPTION_LINES"

def test_second_top_level_breach_auto_approves_normal_lines():
    lines = [
        ExpenseLineResult(
            line_id="L01",
            category="TRAVEL",
            amount=Decimal("3000"),
            eligible_amount=Decimal("3000"),
        ),
        ExpenseLineResult(
            line_id="L02",
            category="FOOD",
            amount=Decimal("2000"),
            eligible_amount=Decimal("2000"),
        ),
    ]

    workflow = create_workflow(lines=lines)

    employees = {
        "M01": Employee(
            "M01", "Top Manager", "E5", "CC01", None, "Bengaluru"
        ),
    }

    # First top-level breach.
    escalate_claim(
        workflow,
        employees,
        datetime(2026, 1, 6, 10, 0),
        set(),
        set(),
    )

    # Second top-level breach.
    result = escalate_claim(
        workflow,
        employees,
        datetime(2026, 1, 12, 10, 0),
        set(),
        set(),
    )

    assert result.status == ClaimStatus.APPROVED
    assert result.claim.status == ClaimStatus.APPROVED

    for line in result.claim.line_decisions:
        assert line.decision == ApprovalDecision.AUTO_APPROVED

    assert result.audit_history[-1].action == "AUTO_APPROVED_CLAIM"
