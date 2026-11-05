from datetime import datetime
from decimal import Decimal

import pytest

from common.models import (
    ApprovalStep,
    ApprovalDecision,
    ClaimStatus,
    ClaimWorkflow,
    ValidatedClaim,
    ExpenseLineResult,
)

from module_b_approval.settlement import settle_approved_workflow


def create_approved_workflow():
    claim = ValidatedClaim(
        claim_id="CL100",
        employee_id="E100",
        total_claimed=Decimal("1700"),
        eligible_amount=Decimal("1200"),
        exception_amount=Decimal("500"),
        rejected_amount=Decimal("0"),
        advance_amount=Decimal("300"),
        line_decisions=[
            ExpenseLineResult(
                line_id="L01",
                category="HOTEL",
                amount=Decimal("500"),
                eligible_amount=Decimal("0"),
                exception_amount=Decimal("500"),
                has_exception=True,
                exception_approved=True,
                decision=ApprovalDecision.APPROVE,
            ),
            ExpenseLineResult(
                line_id="L02",
                category="PER_DIEM",
                amount=Decimal("1200"),
                eligible_amount=Decimal("1200"),
                travel_type="DOMESTIC",
                decision=ApprovalDecision.APPROVE,
            ),
        ],
    )

    step = ApprovalStep(
        approver_id="M01",
        approver_role="MANAGER",
        sequence=1,
        status=ApprovalDecision.APPROVE,
        completed_at=datetime(2026, 11, 4, 10, 0),
    )

    return ClaimWorkflow(
        claim=claim,
        approval_chain=[step],
        current_step=1,
        status=ClaimStatus.APPROVED,
    )


def test_approved_workflow_is_settled():
    workflow = create_approved_workflow()

    settlement = settle_approved_workflow(
        workflow,
        datetime(2026, 11, 11, 10, 0),
        set(),
        set(),
    )

    assert settlement.approved_amount == Decimal("1700")
    assert settlement.taxable_amount == Decimal("700")
    assert settlement.advance_amount == Decimal("300")
    assert settlement.payout_amount == Decimal("1400")
    assert settlement.recovery_amount == Decimal("0")

    assert workflow.status == ClaimStatus.SETTLED
    assert workflow.claim.status == ClaimStatus.SETTLED
    assert workflow.audit_history[-1].action == "SETTLED"


def test_late_settlement_records_sla_breach():
    workflow = create_approved_workflow()

    settle_approved_workflow(
        workflow,
        datetime(2026, 11, 12, 10, 0),
        set(),
        set(),
    )

    actions = [
        event.action for event in workflow.audit_history
    ]

    assert "SETTLEMENT_SLA_BREACHED" in actions
    assert "SETTLED" in actions
    assert workflow.status == ClaimStatus.SETTLED


def test_unapproved_claim_cannot_be_settled():
    workflow = create_approved_workflow()
    workflow.status = ClaimStatus.PENDING_APPROVAL

    with pytest.raises(ValueError, match="Only approved claims"):
        settle_approved_workflow(
            workflow,
            datetime(2026, 11, 11, 10, 0),
            set(),
            set(),
        )