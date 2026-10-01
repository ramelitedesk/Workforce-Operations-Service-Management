from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from leave.models import LeaveRequest, LeaveStatus
from scheduling.services import (
    check_employee_availability,
    check_employee_schedule_conflict,
)
from services.eligibility import get_eligible_employees
from workorders.models import WorkOrder

from .models import (
    AssignmentStatus,
    WorkOrderAssignment,
)


def employee_has_approved_leave(
    employee,
    scheduled_start,
    scheduled_end,
):
    """
    Check whether an employee has approved leave
    during the requested work-order period.
    """

    if not scheduled_start or not scheduled_end:
        return False

    leave_exists = LeaveRequest.objects.filter(
        employee=employee,
        status=LeaveStatus.APPROVED,
        start_date__lte=scheduled_end.date(),
        end_date__gte=scheduled_start.date(),
    ).exists()

    return leave_exists


def employee_is_available_for_work_order(
    employee,
    scheduled_start,
    scheduled_end,
):
    """
    Check availability, existing schedule conflicts,
    and approved leave.
    """

    if not scheduled_start or not scheduled_end:
        return False

    # Employee availability
    if not check_employee_availability(
        employee,
        scheduled_start,
        scheduled_end,
    ):
        return False

    # Existing schedule conflict
    if check_employee_schedule_conflict(
        employee,
        scheduled_start,
        scheduled_end,
    ):
        return False

    # Approved leave
    if employee_has_approved_leave(
        employee,
        scheduled_start,
        scheduled_end,
    ):
        return False

    return True


def get_assignment_candidates(work_order):
    """
    Return employees who satisfy the service skill/certification
    requirements and are available for the scheduled period.
    """

    if not work_order.service:

        return []

    eligible_employees = get_eligible_employees(
        work_order.service
    )

    if (
        not work_order.scheduled_start
        or not work_order.scheduled_end
    ):
        return eligible_employees

    candidates = []

    for employee in eligible_employees:

        if employee_is_available_for_work_order(
            employee,
            work_order.scheduled_start,
            work_order.scheduled_end,
        ):
            candidates.append(employee)

    return candidates


@transaction.atomic
def assign_employee_to_work_order(
    work_order,
    employee,
    assigned_by=None,
    assignment_reason="",
    notes="",
):
    """
    Create an assignment after validating the employee.
    """

    if not work_order:

        raise ValidationError(
            "A work order is required."
        )

    if not employee:

        raise ValidationError(
            "An employee is required."
        )

    # -------------------------------------------------
    # Company validation
    # -------------------------------------------------

    if work_order.company_id != employee.company_id:

        raise ValidationError(
            "The employee and work order must belong "
            "to the same company."
        )

    # -------------------------------------------------
    # Employee status
    # -------------------------------------------------

    if employee.status != "ACTIVE":

        raise ValidationError(
            "Only active employees can be assigned."
        )

    # -------------------------------------------------
    # Service eligibility
    # -------------------------------------------------

    if work_order.service:

        eligible_employees = get_eligible_employees(
            work_order.service
        )

        eligible_ids = {
            employee.id
            for employee in eligible_employees
        }

        if employee.id not in eligible_ids:

            raise ValidationError(
                "The employee does not satisfy the "
                "service skill/certification requirements."
            )

    # -------------------------------------------------
    # Schedule availability
    # -------------------------------------------------

    if (
        work_order.scheduled_start
        and work_order.scheduled_end
    ):

        if not employee_is_available_for_work_order(
            employee,
            work_order.scheduled_start,
            work_order.scheduled_end,
        ):

            raise ValidationError(
                "The employee is not available for "
                "the scheduled work-order time."
            )

    # -------------------------------------------------
    # Existing active assignment
    # -------------------------------------------------

    existing_assignment = (
        WorkOrderAssignment.objects
        .filter(
            work_order=work_order,
            employee=employee,
            status__in=[
                AssignmentStatus.PROPOSED,
                AssignmentStatus.ASSIGNED,
                AssignmentStatus.ACCEPTED,
            ],
        )
        .first()
    )

    if existing_assignment:

        raise ValidationError(
            "This employee is already actively assigned "
            "to this work order."
        )

    # -------------------------------------------------
    # Create assignment
    # -------------------------------------------------

    assignment = WorkOrderAssignment.objects.create(
        company=work_order.company,
        work_order=work_order,
        employee=employee,
        assigned_by=assigned_by,
        status=AssignmentStatus.ASSIGNED,
        assignment_reason=assignment_reason,
        notes=notes,
    )

    # -------------------------------------------------
    # Update Work Order
    # -------------------------------------------------

    work_order.assigned_employee = employee

    if work_order.status in [
        "DRAFT",
        "PENDING",
    ]:
        work_order.status = "ASSIGNED"

    work_order.save(
        update_fields=[
            "assigned_employee",
            "status",
            "updated_at",
        ]
    )

    return assignment