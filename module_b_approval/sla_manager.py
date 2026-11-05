
from datetime import datetime, timedelta, date


def is_working_day(
    check_date: date,
    holidays: set[date],
    approver_leave: set[date]
) -> bool:

    # Saturday = 5, Sunday = 6
    if check_date.weekday() >= 5:
        return False

    if check_date in holidays:
        return False

    if check_date in approver_leave:
        return False

    return True


def add_working_days(
    start: datetime,
    number_of_days: int,
    holidays: set[date],
    approver_leave: set[date]
) -> datetime:

    current = start
    days_added = 0

    while days_added < number_of_days:
        current += timedelta(days=1)

        if is_working_day(
            current.date(),
            holidays,
            approver_leave
        ):
            days_added += 1

    return current


def calculate_deadline(
    assigned_at: datetime,
    holidays: set[date],
    approver_leave: set[date],
    sla_days: int = 3
) -> datetime:

    return add_working_days(
        assigned_at,
        sla_days,
        holidays,
        approver_leave
    )


def is_sla_breached(
    current_time: datetime,
    deadline: datetime
) -> bool:

    return current_time > deadline


def assign_approval_step(
    step,
    assigned_at: datetime,
    holidays: set[date],
    approver_leave: set[date]
):

    step.assigned_at = assigned_at

    step.deadline = calculate_deadline(
        assigned_at,
        holidays,
        approver_leave
    )

    return step
