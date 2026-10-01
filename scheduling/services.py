from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import WorkSchedule


def check_employee_schedule_conflict(
    employee,
    scheduled_start,
    scheduled_end,
    exclude_schedule_id=None,
):
    """
    Check whether an employee already has another schedule
    overlapping the requested time period.
    """

    schedules = WorkSchedule.objects.filter(
        employee=employee,
    ).filter(
        Q(scheduled_start__lt=scheduled_end)
        & Q(scheduled_end__gt=scheduled_start)
    )

    if exclude_schedule_id:
        schedules = schedules.exclude(
            id=exclude_schedule_id
        )

    return schedules.exists()


def check_employee_availability(
    employee,
    scheduled_start,
    scheduled_end,
):
    """
    Check whether the employee is available for the entire
    requested scheduling period.
    """

    if scheduled_start.date() != scheduled_end.date():
        return False

    weekday = scheduled_start.weekday()

    availability = employee.availability.filter(
        weekday=weekday,
        is_available=True,
        start_time__lte=scheduled_start.time(),
        end_time__gte=scheduled_end.time(),
    )

    return availability.exists()


def validate_schedule(
    employee,
    scheduled_start,
    scheduled_end,
    exclude_schedule_id=None,
):
    """
    Validate whether an employee can be scheduled
    for the requested time period.
    """

    errors = {}

    if not scheduled_start or not scheduled_end:
        errors["scheduled_start"] = (
            "Scheduled start and end times are required."
        )
        raise ValidationError(errors)

    if scheduled_start >= scheduled_end:
        errors["scheduled_end"] = (
            "Scheduled end time must be after scheduled start time."
        )
        raise ValidationError(errors)

    if employee.status != "ACTIVE":
        errors["employee"] = (
            "Only active employees can be scheduled."
        )

    if scheduled_start.date() != scheduled_end.date():
        errors["scheduled_end"] = (
            "A schedule must start and end on the same date."
        )

    if not check_employee_availability(
        employee,
        scheduled_start,
        scheduled_end,
    ):
        errors["scheduled_start"] = (
            "The employee is not available during the requested time."
        )

    if check_employee_schedule_conflict(
        employee,
        scheduled_start,
        scheduled_end,
        exclude_schedule_id=exclude_schedule_id,
    ):
        errors["scheduled_start"] = (
            "The employee already has another schedule "
            "during the requested time."
        )

    if errors:
        raise ValidationError(errors)

    return True