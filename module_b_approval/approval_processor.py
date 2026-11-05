
from datetime import datetime

from common.models import (
    ClaimWorkflow,
    ApprovalDecision,
    ClaimStatus,
    AuditEvent,
)


def process_approval(
    workflow: ClaimWorkflow,
    approver_id: str,
    command: str,
    current_time: datetime,
    remarks: str = "",
):
    """Process an APPROVE, REJECT, or RETURN command."""

    command = command.upper().strip()

    # Check whether the claim is awaiting approval.
    if workflow.status != ClaimStatus.PENDING_APPROVAL:
        raise ValueError("Claim is not awaiting approval")

    # Check whether an approval step is available.
    if workflow.current_step >= len(workflow.approval_chain):
        raise ValueError("No pending approval step")

    step = workflow.approval_chain[workflow.current_step]

    # Only the assigned approver can take action.
    if step.approver_id != approver_id:
        raise ValueError("This claim is assigned to another approver")

    # Validate the command.
    if command not in ("APPROVE", "REJECT", "RETURN"):
        raise ValueError("Invalid approval command")

    step.completed_at = current_time

    if command == "APPROVE":

        step.status = ApprovalDecision.APPROVE
        workflow.current_step += 1

        # Check whether all approvers have approved.
        if workflow.current_step == len(workflow.approval_chain):
            workflow.status = ClaimStatus.APPROVED
            workflow.claim.status = ClaimStatus.APPROVED
        else:
            workflow.status = ClaimStatus.PENDING_APPROVAL
            workflow.claim.status = ClaimStatus.PENDING_APPROVAL

        # An approval breaks consecutive top-level escalations.
        workflow.consecutive_top_escalations = 0

    elif command == "REJECT":

        step.status = ApprovalDecision.REJECT
        workflow.status = ClaimStatus.REJECTED
        workflow.claim.status = ClaimStatus.REJECTED

        workflow.consecutive_top_escalations = 0

    elif command == "RETURN":

        step.status = ApprovalDecision.RETURN
        workflow.status = ClaimStatus.RETURNED
        workflow.claim.status = ClaimStatus.RETURNED
        workflow.return_count += 1

        workflow.consecutive_top_escalations = 0

    # Record the action in the audit history.
    workflow.audit_history.append(
        AuditEvent(
            claim_id=workflow.claim.claim_id,
            action=command,
            performed_by=approver_id,
            timestamp=current_time,
            remarks=remarks,
        )
    )

    return workflow


def resubmit_workflow(
    workflow: ClaimWorkflow,
    resubmitted_at: datetime,
):
    """Restart the approval process after a claim is returned."""

    if workflow.status != ClaimStatus.RETURNED:
        raise ValueError("Only returned claims can be resubmitted")

    # Reset all approval steps and their SLA information.
    for step in workflow.approval_chain:
        step.status = ApprovalDecision.PENDING
        step.assigned_at = None
        step.deadline = None
        step.completed_at = None

    # Start again from the first approver.
    workflow.current_step = 0
    workflow.status = ClaimStatus.PENDING_APPROVAL
    workflow.claim.status = ClaimStatus.PENDING_APPROVAL

    # Reset consecutive top-level escalations.
    workflow.consecutive_top_escalations = 0

    # Record resubmission.
    workflow.audit_history.append(
        AuditEvent(
            claim_id=workflow.claim.claim_id,
            action="RESUBMITTED",
            performed_by=workflow.claim.employee_id,
            timestamp=resubmitted_at,
            remarks="Claim resubmitted after corrections",
        )
    )

    return workflow

def print_audit_trail(workflow):
    """Print the complete audit history of a claim."""

    print("\n========== CLAIM AUDIT TRAIL ==========")
    print(f"Claim ID: {workflow.claim.claim_id}")
    print("---------------------------------------")

    if not workflow.audit_history:
        print("No audit events recorded.")
        return

    for number, event in enumerate(workflow.audit_history, start=1):
        print(f"\nEvent {number}")
        print(f"Action      : {event.action}")
        print(f"Performed by: {event.performed_by}")
        print(f"Timestamp   : {event.timestamp}")
        print(f"Remarks     : {event.remarks}")

    print("\n=======================================")
