from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Company
from workforce.models import Employee
from workorders.models import WorkOrder


class ScheduleStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planned"
    CONFIRMED = "CONFIRMED", "Confirmed"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class WorkSchedule(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="work_schedules",
    )

    work_order = models.OneToOneField(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="schedule",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=ScheduleStatus.choices,
        default=ScheduleStatus.PLANNED,
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_schedules",
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_start"]

    def clean(self):
        errors = {}

        # -------------------------------
        # Date/time validation
        # -------------------------------
        if self.scheduled_start and self.scheduled_end:

            if self.scheduled_start >= self.scheduled_end:
                errors["scheduled_end"] = (
                    "Scheduled end time must be after scheduled start time."
                )

            if (
                self.scheduled_start.date()
                != self.scheduled_end.date()
            ):
                errors["scheduled_end"] = (
                    "A schedule must start and end on the same date."
                )

        # -------------------------------
        # Company validation
        # -------------------------------
        if self.company_id and self.employee_id:

            if self.employee.company_id != self.company_id:
                errors["employee"] = (
                    "The employee must belong to the selected company."
                )

        if self.company_id and self.work_order_id:

            if self.work_order.company_id != self.company_id:
                errors["work_order"] = (
                    "The work order must belong to the selected company."
                )

        # -------------------------------
        # Employee availability/conflict
        # -------------------------------
        if (
            self.employee_id
            and self.scheduled_start
            and self.scheduled_end
            and not errors
        ):
            from .services import validate_schedule

            try:
                validate_schedule(
                    employee=self.employee,
                    scheduled_start=self.scheduled_start,
                    scheduled_end=self.scheduled_end,
                    exclude_schedule_id=self.pk,
                )

            except ValidationError as exc:
                if hasattr(exc, "message_dict"):
                    errors.update(exc.message_dict)
                else:
                    errors["employee"] = exc.messages

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.work_order.work_order_number} - "
            f"{self.employee.employee_id}"
        )

class EmployeeAvailability(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="availability",
    )

    weekday = models.PositiveSmallIntegerField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ]
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_available = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "employee",
            "weekday",
            "start_time",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "weekday",
                    "start_time",
                    "end_time",
                ],
                name="unique_employee_availability_period",
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.get_weekday_display()} "
            f"{self.start_time} - {self.end_time}"
        )