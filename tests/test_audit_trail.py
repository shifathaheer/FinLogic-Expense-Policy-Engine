
from types import SimpleNamespace
from datetime import datetime

from module_b_approval.approval_processor import print_audit_trail


def test_print_audit_trail(capsys):
    event = SimpleNamespace(
        action="APPROVE",
        performed_by="EMP002",
        timestamp=datetime(2026, 11, 5, 10, 30),
        remarks="Claim approved"
    )

    workflow = SimpleNamespace(
        claim=SimpleNamespace(claim_id="CLM001"),
        audit_history=[event]
    )

    print_audit_trail(workflow)

    output = capsys.readouterr().out

    assert "CLM001" in output
    assert "APPROVE" in output
    assert "EMP002" in output
    assert "Claim approved" in output


def test_print_audit_trail_when_empty(capsys):
    workflow = SimpleNamespace(
        claim=SimpleNamespace(claim_id="CLM002"),
        audit_history=[]
    )

    print_audit_trail(workflow)

    output = capsys.readouterr().out

    assert "CLM002" in output
    assert "No audit events recorded." in output
