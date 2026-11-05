
from common.models import (
    ApprovalStep,
    ApprovalDecision,
    ClaimStatus,
    AuditEvent,
)

from module_b_approval.sla_manager import (
    is_sla_breached,
    assign_approval_step,
)


def escalate_claim(workflow, employees, current_time, holidays, approver_leave):

    if workflow.status != ClaimStatus.PENDING_APPROVAL:
        raise ValueError("Claim is not awaiting approval")

    if workflow.current_step >= len(workflow.approval_chain):
        raise ValueError("No pending approval step")

    current_step = workflow.approval_chain[workflow.current_step]

    if current_step.deadline is None:
        raise ValueError("Current approval step has no deadline")

    if not is_sla_breached(current_time, current_step.deadline):
        raise ValueError("Approval deadline has not been breached")

    current_approver = employees.get(current_step.approver_id)

    if current_approver is None:
        raise ValueError("Current approver not found")

    manager_id = current_approver.manager_id

    # CASE 1: Top-level approver has no manager.
    if manager_id is None:

        workflow.consecutive_top_escalations += 1

        # First top-level breach: give another 3 working days.
        if workflow.consecutive_top_escalations < 2:

            assign_approval_step(
                current_step,
                current_time,
                holidays,
                approver_leave,
            )

            workflow.audit_history.append(
                AuditEvent(
                    claim_id=workflow.claim.claim_id,
                    action="TOP_LEVEL_ESCALATION_RETRY",
                    performed_by="SYSTEM",
                    timestamp=current_time,
                    remarks="First top-level SLA breach. Approval deadline reset.",
                )
            )

            return workflow

        # Second top-level breach: decide each expense line separately.
        has_returned_lines = False

        for line in workflow.claim.line_decisions:

            if line.has_exception or line.exception_amount > 0:
                line.decision = ApprovalDecision.RETURN
                has_returned_lines = True

            else:
                line.decision = ApprovalDecision.AUTO_APPROVED

        current_step.status = ApprovalDecision.ESCALATED
        current_step.completed_at = current_time

        if has_returned_lines or (
            not workflow.claim.line_decisions
            and workflow.claim.exception_amount > 0
        ):
            workflow.status = ClaimStatus.RETURNED
            workflow.claim.status = ClaimStatus.RETURNED

            action = "RETURNED_EXCEPTION_LINES"
            remarks = (
                "Second top-level SLA breach. "
                "Non-exception lines auto-approved; "
                "exception lines returned."
            )

        else:
            workflow.status = ClaimStatus.APPROVED
            workflow.claim.status = ClaimStatus.APPROVED

            action = "AUTO_APPROVED_CLAIM"
            remarks = (
                "Second top-level SLA breach. "
                "All non-exception lines auto-approved."
            )

        workflow.audit_history.append(
            AuditEvent(
                claim_id=workflow.claim.claim_id,
                action=action,
                performed_by="SYSTEM",
                timestamp=current_time,
                remarks=remarks,
            )
        )

        return workflow

    # CASE 2: Normal escalation to the approver's manager.
    manager = employees.get(manager_id)

    if manager is None:
        raise ValueError("Escalation manager not found")

    if manager_id == current_step.approver_id:
        raise ValueError("Approver cannot be escalated to themselves")

    # Check whether this manager is already waiting in the approval chain.
    existing_step = next(
        (
            step
            for step in workflow.approval_chain
            if step.approver_id == manager_id
            and step.status == ApprovalDecision.PENDING
        ),
        None,
    )

    # Reuse the existing step instead of adding a duplicate approver.
    if existing_step is not None:

        current_step.status = ApprovalDecision.ESCALATED
        current_step.completed_at = current_time

        workflow.current_step = workflow.approval_chain.index(existing_step)
        workflow.consecutive_top_escalations = 0

        assign_approval_step(
            existing_step,
            current_time,
            holidays,
            approver_leave,
        )

        workflow.audit_history.append(
            AuditEvent(
                claim_id=workflow.claim.claim_id,
                action="ESCALATED",
                performed_by="SYSTEM",
                timestamp=current_time,
                remarks=(
                    f"Approver {current_step.approver_id} missed deadline. "
                    f"Assigned to existing approver {manager_id}."
                ),
            )
        )

        return workflow

    # No existing step: create a new escalation step.
    workflow.consecutive_top_escalations = 0

    current_step.status = ApprovalDecision.ESCALATED
    current_step.completed_at = current_time

    escalated_step = ApprovalStep(
        approver_id=manager_id,
        approver_role="ESCALATED_MANAGER",
        sequence=current_step.sequence + 1,
    )

    assign_approval_step(
        escalated_step,
        current_time,
        holidays,
        approver_leave,
    )

    insert_position = workflow.current_step + 1

    workflow.approval_chain.insert(
        insert_position,
        escalated_step,
    )

    # Update approval sequence numbers.
    for index, step in enumerate(workflow.approval_chain):
        step.sequence = index + 1

    workflow.current_step = insert_position

    workflow.audit_history.append(
        AuditEvent(
            claim_id=workflow.claim.claim_id,
            action="ESCALATED",
            performed_by="SYSTEM",
            timestamp=current_time,
            remarks=(
                f"Approver {current_step.approver_id} missed deadline. "
                f"Escalated to manager {manager_id}."
            ),
        )
    )

    return workflow
