
from datetime import datetime
from decimal import Decimal

import pytest

from common.models import (
    Employee,
    ValidatedClaim,
    ClaimWorkflow,
    ClaimStatus
)

from module_b_approval.approval_chain import build_approval_chain

from module_b_approval.approval_processor import (
    process_approval,
    resubmit_workflow
)


# Create sample employees for testing.
def create_employees():

    return {
        "E101": Employee(
            "E101", "Employee", "E2", "CC01", "M01", "Bangalore"
        ),

        "M01": Employee(
            "M01", "Manager", "E4", "CC01", "CEO", "Bangalore"
        ),

        "H01": Employee(
            "H01", "Head", "E5", "CC01", "CEO", "Bangalore"
        ),

        "FC01": Employee(
            "FC01", "Finance Controller", "E5", "CC02", "CEO", "Bangalore"
        ),

        "E501": Employee(
            "E501", "E5 Approver", "E5", "CC03", "CEO", "Bangalore"
        ),

        "CEO": Employee(
            "CEO", "CEO", "E5", "CC00", None, "Bangalore"
        )
    }


# Create a sample claim.
def create_claim(amount, exception_amount=Decimal("0")):

    amount = Decimal(str(amount))
    exception_amount = Decimal(str(exception_amount))

    return ValidatedClaim(
        claim_id="CL001",
        employee_id="E101",
        total_claimed=amount,
        eligible_amount=amount - exception_amount,
        exception_amount=exception_amount,
        rejected_amount=Decimal("0")
    )


# Build an approval chain for a sample claim.
def build_chain(claim, employees):

    return build_approval_chain(
        claim,
        employees,
        {"CC01": "H01"},
        "FC01",
        "E501"
    )


# 1. Test manager and cost-centre head approval.
def test_manager_approval():

    employees = create_employees()
    claim = create_claim(35000)

    chain = build_chain(claim, employees)

    workflow = ClaimWorkflow(
        claim=claim,
        approval_chain=chain
    )

    workflow.status = ClaimStatus.PENDING_APPROVAL

    process_approval(
        workflow,
        "M01",
        "APPROVE",
        datetime(2026, 11, 4, 10, 0)
    )

    assert workflow.current_step == 1
    assert workflow.status == ClaimStatus.PENDING_APPROVAL

    process_approval(
        workflow,
        "H01",
        "APPROVE",
        datetime(2026, 11, 4, 11, 0)
    )

    assert workflow.status == ClaimStatus.APPROVED
    assert len(workflow.audit_history) == 2


# 2. Exactly Rs. 10,000 requires only manager approval.
def test_exactly_10000_requires_only_manager():

    employees = create_employees()
    claim = create_claim(10000)

    chain = build_chain(claim, employees)

    assert len(chain) == 1
    assert chain[0].approver_id == "M01"


# 3. Exactly Rs. 50,000 requires manager and cost-centre head.
def test_exactly_50000_requires_manager_and_head():

    employees = create_employees()
    claim = create_claim(50000)

    chain = build_chain(claim, employees)

    assert len(chain) == 2
    assert chain[0].approver_id == "M01"
    assert chain[1].approver_id == "H01"


# 4. Above Rs. 50,000 also requires finance controller.
def test_above_50000_requires_finance_controller():

    employees = create_employees()
    claim = create_claim(50001)

    chain = build_chain(claim, employees)

    assert len(chain) == 3
    assert chain[2].approver_id == "FC01"


# 5. An exception requires E5 approval.
def test_exception_requires_e5_approval():

    employees = create_employees()

    claim = create_claim(
        8000,
        exception_amount=Decimal("1000")
    )

    chain = build_chain(claim, employees)

    assert len(chain) == 2
    assert chain[1].approver_id == "E501"
    assert chain[1].approver_role == "E5_APPROVER"


# 6. Exception approver must have grade E5.
def test_exception_approver_must_be_grade_e5():

    employees = create_employees()
    employees["E501"].grade = "E4"

    claim = create_claim(
        8000,
        exception_amount=Decimal("1000")
    )

    with pytest.raises(ValueError, match="must have grade E5"):

        build_chain(claim, employees)


# 7. An employee cannot approve their own claim.
def test_employee_cannot_approve_own_claim():

    employees = create_employees()
    employees["E101"].manager_id = "E101"

    claim = create_claim(8000)

    with pytest.raises(ValueError, match="own claim"):

        build_chain(claim, employees)


# 8. Peer approval is not allowed.
def test_peer_cannot_approve_claim():

    employees = create_employees()
    employees["H01"].manager_id = "M01"

    claim = create_claim(15000)

    with pytest.raises(ValueError, match="Peer approval not allowed"):

        build_chain(claim, employees)


# 9. Test rejection of a claim.
def test_reject_claim():

    employees = create_employees()
    claim = create_claim(8000)

    chain = build_chain(claim, employees)

    workflow = ClaimWorkflow(
        claim=claim,
        approval_chain=chain
    )

    workflow.status = ClaimStatus.PENDING_APPROVAL

    process_approval(
        workflow,
        "M01",
        "REJECT",
        datetime(2026, 11, 5, 10, 0)
    )

    assert workflow.status == ClaimStatus.REJECTED
    assert workflow.claim.status == ClaimStatus.REJECTED
    assert workflow.approval_chain[0].status.value == "REJECT"
    assert workflow.audit_history[-1].action == "REJECT"


# 10. Test returning a claim for correction.
def test_return_claim():

    employees = create_employees()
    claim = create_claim(8000)

    chain = build_chain(claim, employees)

    workflow = ClaimWorkflow(
        claim=claim,
        approval_chain=chain
    )

    workflow.status = ClaimStatus.PENDING_APPROVAL

    process_approval(
        workflow,
        "M01",
        "RETURN",
        datetime(2026, 11, 5, 10, 0),
        remarks="Please correct the missing receipt"
    )

    assert workflow.status == ClaimStatus.RETURNED
    assert workflow.claim.status == ClaimStatus.RETURNED
    assert workflow.return_count == 1
    assert workflow.audit_history[-1].remarks == "Please correct the missing receipt"


# 11. Test resubmission of a returned claim.
def test_resubmit_returned_claim():

    employees = create_employees()
    claim = create_claim(8000)

    chain = build_chain(claim, employees)

    workflow = ClaimWorkflow(
        claim=claim,
        approval_chain=chain
    )

    workflow.status = ClaimStatus.PENDING_APPROVAL

    process_approval(
        workflow,
        "M01",
        "RETURN",
        datetime(2026, 11, 5, 10, 0)
    )

    resubmit_workflow(
        workflow,
        datetime(2026, 11, 6, 10, 0)
    )

    assert workflow.status == ClaimStatus.PENDING_APPROVAL
    assert workflow.claim.status == ClaimStatus.PENDING_APPROVAL
    assert workflow.current_step == 0
    assert workflow.return_count == 1
    assert workflow.approval_chain[0].status.value == "PENDING"
    assert workflow.audit_history[-1].action == "RESUBMITTED"
