
from datetime import datetime
from decimal import Decimal

from common.models import (
    SettlementResult,
    AuditEvent,
    ClaimStatus,
)

from module_b_approval.sla_manager import add_working_days
from module_b_approval.tax_calculator import calculate_taxable_amount


def calculate_settlement(
    claim_id,
    approved_amount,
    taxable_amount,
    advance_amount,
    settlement_date=None,
):
    approved_amount = Decimal(str(approved_amount))
    taxable_amount = Decimal(str(taxable_amount))
    advance_amount = Decimal(str(advance_amount))

    if approved_amount < 0 or taxable_amount < 0 or advance_amount < 0:
        raise ValueError("Settlement amounts cannot be negative")

    payout = max(Decimal("0"), approved_amount - advance_amount)
    recovery = max(Decimal("0"), advance_amount - approved_amount)

    return SettlementResult(
        claim_id=claim_id,
        approved_amount=approved_amount,
        taxable_amount=taxable_amount,
        advance_amount=advance_amount,
        payout_amount=payout,
        recovery_amount=recovery,
        settlement_date=settlement_date,
    )


def calculate_settlement_deadline(
    final_approval_time,
    holidays,
    approver_leave,
):
    return add_working_days(
        final_approval_time,
        5,
        holidays,
        approver_leave,
    )


def record_settlement_audit(
    workflow,
    performed_by,
    current_time,
    remarks="",
):
    event = AuditEvent(
        claim_id=workflow.claim.claim_id,
        action="SETTLED",
        performed_by=performed_by,
        timestamp=current_time,
        remarks=remarks,
    )

    workflow.audit_history.append(event)
    return event


def settle_approved_workflow(
    workflow,
    current_time,
    holidays,
    approver_leave,
):
    if workflow.status != ClaimStatus.APPROVED:
        raise ValueError("Only approved claims can be settled")

    completed_steps = [
        step.completed_at
        for step in workflow.approval_chain
        if step.completed_at is not None
    ]

    if not completed_steps:
        raise ValueError("Final approval time not found")

    final_approval_time = max(completed_steps)

    if current_time < final_approval_time:
        raise ValueError("Settlement time cannot be before final approval")

    deadline = calculate_settlement_deadline(
        final_approval_time,
        holidays,
        approver_leave,
    )

    # Start with the eligible amount.
    approved_amount = Decimal(str(workflow.claim.eligible_amount))

    # Add only E5-approved exceptions that were not rejected or returned.
    for line in workflow.claim.line_decisions:
        if getattr(line, "exception_approved", None) is not True:
            continue

        decision = getattr(line, "decision", None)
        decision_value = getattr(decision, "value", decision)

        if str(decision_value).upper() in ("REJECT", "RETURN"):
            continue

        approved_amount += Decimal(str(line.exception_amount))

    taxable_amount = calculate_taxable_amount(
        workflow.claim.line_decisions
    )

    settlement = calculate_settlement(
        claim_id=workflow.claim.claim_id,
        approved_amount=approved_amount,
        taxable_amount=taxable_amount,
        advance_amount=workflow.claim.advance_amount,
        settlement_date=current_time.date(),
    )

    if current_time > deadline:
        workflow.audit_history.append(
            AuditEvent(
                claim_id=workflow.claim.claim_id,
                action="SETTLEMENT_SLA_BREACHED",
                performed_by="SYSTEM",
                timestamp=current_time,
                remarks="Settlement completed after five working days",
            )
        )

    workflow.status = ClaimStatus.SETTLED
    workflow.claim.status = ClaimStatus.SETTLED

    record_settlement_audit(
        workflow,
        "SYSTEM",
        current_time,
        "Claim settlement completed",
    )

    return settlement
