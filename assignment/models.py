from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Company
from workforce.models import Employee
from workorders.models import WorkOrder


class AssignmentStatus(models.TextChoices):
    PROPOSED = "PROPOSED", "Proposed"
    ASSIGNED = "ASSIGNED", "Assigned"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"


class WorkOrderAssignment(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="work_order_assignments",
    )

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="work_order_assignments",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_work_order_assignments",
    )

    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.PROPOSED,
    )

    assignment_reason = models.TextField(
        blank=True,
        help_text=(
            "Reason why this employee was selected "
            "for the work order."
        ),
    )

    notes = models.TextField(
        blank=True,
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-assigned_at",
        ]

    def clean(self):

        errors = {}

        # -------------------------------------------------
        # Company validation
        # -------------------------------------------------

        if self.work_order_id and self.company_id:

            if self.work_order.company_id != self.company_id:
                errors["work_order"] = (
                    "The work order must belong to the selected company."
                )

        if self.employee_id and self.company_id:

            if self.employee.company_id != self.company_id:
                errors["employee"] = (
                    "The employee must belong to the selected company."
                )

        # -------------------------------------------------
        # Employee status
        # -------------------------------------------------

        if self.employee_id:

            if self.employee.status != "ACTIVE":
                errors["employee"] = (
                    "Only active employees can be assigned "
                    "to work orders."
                )

        # -------------------------------------------------
        # Duplicate active assignment
        # -------------------------------------------------

        if self.work_order_id and self.employee_id:

            existing_assignment = (
                WorkOrderAssignment.objects
                .filter(
                    work_order=self.work_order,
                    employee=self.employee,
                )
                .filter(
                    status__in=[
                        AssignmentStatus.PROPOSED,
                        AssignmentStatus.ASSIGNED,
                        AssignmentStatus.ACCEPTED,
                    ]
                )
            )

            if self.pk:
                existing_assignment = (
                    existing_assignment.exclude(pk=self.pk)
                )

            if existing_assignment.exists():

                errors["employee"] = (
                    "This employee already has an active "
                    "assignment for this work order."
                )

        # -------------------------------------------------
        # Work Order status validation
        # -------------------------------------------------

        if self.work_order_id:

            if self.work_order.status == "CANCELLED":

                errors["work_order"] = (
                    "Cancelled work orders cannot be assigned."
                )

            elif self.work_order.status == "CLOSED":

                errors["work_order"] = (
                    "Closed work orders cannot be assigned."
                )

        # -------------------------------------------------

        if errors:
            raise ValidationError(errors)

    def __str__(self):

        return (
            f"{self.work_order.work_order_number} - "
            f"{self.employee.employee_id} - "
            f"{self.get_status_display()}"
        )