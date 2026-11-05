
from datetime import datetime, date

from module_b_approval.sla_manager import (
    calculate_deadline,
    is_sla_breached
)


# 1. Test three-working-day SLA with a holiday.
def test_three_working_day_sla():

    assigned_at = datetime(2026, 11, 9, 10, 0)

    holidays = {
        date(2026, 11, 11)
    }

    approver_leave = set()

    deadline = calculate_deadline(
        assigned_at,
        holidays,
        approver_leave
    )

    assert deadline == datetime(2026, 11, 13, 10, 0)


# 2. Test whether the SLA deadline has been breached.
def test_sla_breach():

    deadline = datetime(2026, 11, 13, 10, 0)

    assert is_sla_breached(
        datetime(2026, 11, 13, 10, 1),
        deadline
    )

    assert not is_sla_breached(
        datetime(2026, 11, 13, 10, 0),
        deadline
    )


# 3. Test that weekends are excluded.
def test_weekend_exclusion():

    assigned_at = datetime(2026, 11, 6, 10, 0)

    deadline = calculate_deadline(
        assigned_at,
        set(),
        set()
    )

    assert deadline == datetime(2026, 11, 11, 10, 0)


# 4. Test that approver leave is excluded.
def test_approver_leave_exclusion():

    assigned_at = datetime(2026, 11, 9, 10, 0)

    leave = {
        date(2026, 11, 10)
    }

    deadline = calculate_deadline(
        assigned_at,
        set(),
        leave
    )

    assert deadline == datetime(2026, 11, 13, 10, 0)


# 5. Test holiday and approver leave together.
def test_holiday_and_approver_leave_exclusion():

    assigned_at = datetime(2026, 11, 9, 10, 0)

    holidays = {
        date(2026, 11, 10)
    }

    approver_leave = {
        date(2026, 11, 11)
    }

    deadline = calculate_deadline(
        assigned_at,
        holidays,
        approver_leave
    )

    # Thursday 12, Friday 13 and Monday 16
    # are the three working days.

    assert deadline == datetime(2026, 11, 16, 10, 0)
