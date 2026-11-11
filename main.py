
from datetime import date, datetime
from decimal import Decimal

from common.models import (
    ExpenseLine,
    Employee,
    ExpenseLineResult,
    ValidatedClaim,
    ClaimWorkflow,
    ClaimStatus,
    ApprovalDecision,
)

from module_a_validation.claim_processor import process_claim

from module_b_approval.approval_chain import build_approval_chain

from module_b_approval.approval_processor import (
    process_approval,
    print_audit_trail,
)

from module_b_approval.settlement import settle_approved_workflow


def main():

    print("\n========== FINLOGIC REIMBURSEMENT SYSTEM ==========")

    # 1. Employee submits an expense
    expense = ExpenseLine(
        line_id="EXP001",
        category="meal",
        expense_date="2026-11-11",
        amount=Decimal("500"),
        currency="INR",
        receipt=True,
        vendor="Demo Restaurant",
        employee_id="E100",
        employee_name="Demo Employee",
    )

    print("\n1. EXPENSE SUBMISSION")
    print("Employee:", expense.employee_name)
    print("Expense:", expense.category)
    print("Amount: Rs.", expense.amount)

    # 2. Module A validates the expense
    print("\n2. MODULE A - EXPENSE VALIDATION")

    validation = process_claim(expense)

    print("Status:", validation["status"])
    print("Eligible amount:", validation["eligible_amount"])
    print("Rejected amount:", validation["rejected_amount"])
    print("Errors:", validation["errors"])

    if validation["status"] != "VALID":
        print("\nClaim cannot proceed because validation failed.")
        return

    # 3. Prepare the validated claim
    line_result = ExpenseLineResult(
        line_id=expense.line_id,
        category=expense.category.upper(),
        amount=expense.amount,
        eligible_amount=validation["eligible_amount"],
        rejected_amount=validation["rejected_amount"],
        expense_date=date.fromisoformat(expense.expense_date),
        decision=ApprovalDecision.PENDING,
    )

    claim = ValidatedClaim(
        claim_id="CL100",
        employee_id="E100",
        total_claimed=expense.amount,
        eligible_amount=validation["eligible_amount"],
        exception_amount=Decimal("0"),
        rejected_amount=validation["rejected_amount"],
        advance_amount=Decimal("0"),
        line_decisions=[line_result],
        status=ClaimStatus.PENDING_APPROVAL,
    )

    # 4. Create employee and manager records
    employee = Employee(
        employee_id="E100",
        name="Demo Employee",
        grade="E2",
        cost_centre="CC100",
        manager_id="M01",
        base_city="Bengaluru",
    )

    manager = Employee(
        employee_id="M01",
        name="Demo Manager",
        grade="E4",
        cost_centre="CC100",
        manager_id="M99",
        base_city="Bengaluru",
    )

    employees = {
        "E100": employee,
        "M01": manager,
    }

    # 5. Module B builds the approval chain
    print("\n3. MODULE B - APPROVAL CHAIN")

    approval_chain = build_approval_chain(
        claim=claim,
        employees=employees,
        cost_centre_heads={},
        finance_controller_id="F01",
        e5_approver_id="E500",
    )

    for step in approval_chain:
        print(
            f"Step {step.sequence}: "
            f"{step.approver_role} - {step.approver_id}"
        )

    workflow = ClaimWorkflow(
        claim=claim,
        approval_chain=approval_chain,
        status=ClaimStatus.PENDING_APPROVAL,
    )

    # 6. Manager approves the claim
    print("\n4. APPROVAL PROCESS")

    approval_time = datetime(2026, 11, 11, 10, 0)

    process_approval(
        workflow=workflow,
        approver_id="M01",
        command="APPROVE",
        current_time=approval_time,
        remarks="Expense verified and approved",
    )

    print("Workflow status:", workflow.status.value)

    # 7. Settle the approved claim
    print("\n5. CLAIM SETTLEMENT")

    settlement = settle_approved_workflow(
        workflow=workflow,
        current_time=datetime(2026, 11, 11, 11, 0),
        holidays=set(),
        approver_leave=set(),
    )

    print("Approved amount: Rs.", settlement.approved_amount)
    print("Taxable amount: Rs.", settlement.taxable_amount)
    print("Advance deducted: Rs.", settlement.advance_amount)
    print("Final payout: Rs.", settlement.payout_amount)
    print("Recovery: Rs.", settlement.recovery_amount)

    # 8. Display audit history
    print("\n6. AUDIT HISTORY")
    print_audit_trail(workflow)

    print("\nFinal claim status:", workflow.status.value)

    print("\n========== FINLOGIC DEMO COMPLETED ==========")


if __name__ == "__main__":
    main()
