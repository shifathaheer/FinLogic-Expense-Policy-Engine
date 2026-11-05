
from common.models import (
    Employee,
    ValidatedClaim,
    ApprovalStep,
    ApprovalDecision
)


def build_approval_chain(
    claim: ValidatedClaim,
    employees: dict[str, Employee],
    cost_centre_heads: dict[str, str],
    finance_controller_id: str,
    e5_approver_id: str
) -> list[ApprovalStep]:

    # Find the employee who submitted the claim.
    employee = employees.get(claim.employee_id)

    if employee is None:
        raise ValueError("Claim employee not found")

    # Calculate the amount that requires approval.
    approval_amount = claim.eligible_amount + claim.exception_amount

    # Check whether any expense line has an exception.
    has_exception = (
        claim.exception_amount > 0
        or any(line.has_exception for line in claim.line_decisions)
    )

    required_approvers = []

    # Every claim requires manager approval.
    if employee.manager_id is None:
        raise ValueError("Employee has no assigned manager")

    required_approvers.append((employee.manager_id, "MANAGER"))

    # Claims above Rs. 10,000 require cost-centre head approval.
    if approval_amount > 10000:
        head_id = cost_centre_heads.get(employee.cost_centre)

        if not head_id:
            raise ValueError("Cost-centre head not configured")

        required_approvers.append((head_id, "COST_CENTRE_HEAD"))

    # Claims above Rs. 50,000 also require finance approval.
    if approval_amount > 50000:
        if not finance_controller_id:
            raise ValueError("Finance controller not configured")

        required_approvers.append(
            (finance_controller_id, "FINANCE_CONTROLLER")
        )

    # Claims containing exceptions require an E5 approver.
    if has_exception:
        approver = employees.get(e5_approver_id)

        if approver is None:
            raise ValueError("E5 approver not found")

        if approver.grade != "E5":
            raise ValueError("Exception approver must have grade E5")

        required_approvers.append((e5_approver_id, "E5_APPROVER"))

    approval_chain = []
    added_approvers = set()

    for approver_id, role in required_approvers:

        # Avoid adding the same person twice.
        if approver_id in added_approvers:
            continue

        approver = employees.get(approver_id)

        if approver is None:
            raise ValueError(f"Approver {approver_id} not found")

        # Employees cannot approve their own claims.
        if approver_id == employee.employee_id:
            raise ValueError("Employee cannot approve their own claim")

        # Peer approval is not allowed.
        if approver.manager_id == employee.manager_id:
            raise ValueError(f"Peer approval not allowed: {approver_id}")

        added_approvers.add(approver_id)

        approval_chain.append(
            ApprovalStep(
                approver_id=approver_id,
                approver_role=role,
                sequence=len(approval_chain) + 1,
                status=ApprovalDecision.PENDING
            )
        )

    return approval_chain
