from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


# 1. Claim status
class ClaimStatus(Enum):
    SUBMITTED = "SUBMITTED"
    VALIDATED = "VALIDATED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    RETURNED = "RETURNED"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    SETTLED = "SETTLED"


# 2. Approval decision
class ApprovalDecision(Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    RETURN = "RETURN"
    PENDING = "PENDING"
    AUTO_APPROVED = "AUTO_APPROVED"
    ESCALATED = "ESCALATED"


# 3. Employee details
@dataclass
class Employee:
    employee_id: str
    name: str
    grade: str
    cost_centre: str
    manager_id: Optional[str]
    base_city: str


# 4. Individual expense validation result
@dataclass
class ExpenseLineResult:
    line_id: str
    category: str
    amount: Decimal
    eligible_amount: Decimal

    # Expense amounts
    exception_amount: Decimal = Decimal("0")
    rejected_amount: Decimal = Decimal("0")

    # Validation information
    rule_ids: list[str] = field(default_factory=list)
    has_exception: bool = False
    exception_approved: Optional[bool] = None

    # Additional expense information
    expense_date: Optional[date] = None
    travel_type: Optional[str] = None  # DOMESTIC / INTERNATIONAL
    details: dict = field(default_factory=dict)

    # Module B approval status
    decision: ApprovalDecision = ApprovalDecision.PENDING


# 5. Validated claim information
@dataclass
class ValidatedClaim:
    claim_id: str
    employee_id: str
    total_claimed: Decimal
    eligible_amount: Decimal
    exception_amount: Decimal
    rejected_amount: Decimal
    line_decisions: list[ExpenseLineResult] = field(default_factory=list)
    advance_amount: Decimal = Decimal("0")
    status: ClaimStatus = ClaimStatus.VALIDATED


# 6. Individual approval step
@dataclass
class ApprovalStep:
    approver_id: str
    approver_role: str
    sequence: int
    status: ApprovalDecision = ApprovalDecision.PENDING
    assigned_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# 7. Audit history
@dataclass
class AuditEvent:
    claim_id: str
    action: str
    performed_by: str
    timestamp: datetime
    remarks: str = ""


# 8. Settlement result
@dataclass
class SettlementResult:
    claim_id: str
    approved_amount: Decimal
    taxable_amount: Decimal
    advance_amount: Decimal
    payout_amount: Decimal
    recovery_amount: Decimal
    settlement_date: Optional[date] = None


# 9. Complete claim workflow
@dataclass
class ClaimWorkflow:
    claim: ValidatedClaim
    approval_chain: list[ApprovalStep] = field(default_factory=list)
    audit_history: list[AuditEvent] = field(default_factory=list)
    current_step: int = 0
    status: ClaimStatus = ClaimStatus.VALIDATED
    return_count: int = 0
    consecutive_top_escalations: int = 0
# Module A - Individual Expense Input
@dataclass
class ExpenseLine:
    line_id: str
    category: str
    expense_date: str
    amount: Decimal
    currency: str

    employee_id: Optional[str] = None
    employee_name: Optional[str] = None

    receipt: bool = False
    trip_reference: Optional[str] = None
    vendor: Optional[str] = None

    travel_type: Optional[str] = None
    travel_duration_hours: Optional[Decimal] = None
    travel_class: Optional[str] = None
    attendees: list = field(default_factory=list)

    eligible_amount: Decimal = Decimal("0.00")
    exception_amount: Decimal = Decimal("0.00")
    rejected_amount: Decimal = Decimal("0.00")

    validation_status: str = "PENDING"
    rule_ids: list = field(default_factory=list)

    exception_flag: bool = False
    exception_approved: Optional[bool] = None

    approved_amount: Decimal = Decimal("0.00")
    policy_rate: Optional[Decimal] = None
    card_rate: Optional[Decimal] = None
    applied_rate: Optional[Decimal] = None

    details: dict = field(default_factory=dict)
