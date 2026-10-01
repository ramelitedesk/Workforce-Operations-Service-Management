from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Company
from workforce.models import Employee
from workorders.models import WorkOrder


class AttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Present"
    ABSENT = "ABSENT", "Absent"
    HALF_DAY = "HALF_DAY", "Half Day"
    ON_LEAVE = "ON_LEAVE", "On Leave"
    HOLIDAY = "HOLIDAY", "Holiday"


class Attendance(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    attendance_date = models.DateField()

    check_in = models.DateTimeField(
        null=True,
        blank=True,
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-attendance_date",
            "employee",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "employee",
                    "attendance_date",
                ],
                name="unique_employee_attendance_per_day",
            )
        ]

    def clean(self):
        errors = {}

        # -----------------------------------------
        # Employee and company validation
        # -----------------------------------------
        if self.employee_id and self.company_id:
            if self.employee.company_id != self.company_id:
                errors["employee"] = (
                    "The employee must belong to the selected company."
                )

        # -----------------------------------------
        # Check-in / check-out validation
        # -----------------------------------------
        if self.check_in and self.check_out:

            if self.check_in >= self.check_out:
                errors["check_out"] = (
                    "Check-out must be after check-in."
                )

        # -----------------------------------------
        # Check-in date validation
        # -----------------------------------------
        if self.check_in:
            if self.check_in.date() != self.attendance_date:
                errors["check_in"] = (
                    "Check-in date must match the attendance date."
                )

        # -----------------------------------------
        # Check-out date validation
        # -----------------------------------------
        if self.check_out:
            if self.check_out.date() != self.attendance_date:
                errors["check_out"] = (
                    "Check-out date must match the attendance date."
                )

        # -----------------------------------------
        # Status validation
        # -----------------------------------------
        if self.status in [
            AttendanceStatus.ABSENT,
            AttendanceStatus.ON_LEAVE,
            AttendanceStatus.HOLIDAY,
        ]:
            if self.check_in or self.check_out:
                errors["status"] = (
                    "Check-in and check-out should be empty "
                    "for this attendance status."
                )

        # -----------------------------------------
        # Present / Half Day validation
        # -----------------------------------------
        if self.status in [
            AttendanceStatus.PRESENT,
            AttendanceStatus.HALF_DAY,
        ]:
            if not self.check_in:
                errors["check_in"] = (
                    "Check-in is required for Present or Half Day attendance."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.attendance_date}"
        )


class TimeEntry(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    description = models.TextField(
        blank=True,
    )

    regular_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
    )

    overtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
    )

    billable = models.BooleanField(
        default=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-start_time",
        ]

    def clean(self):
        errors = {}

        # -----------------------------------------
        # Employee and company validation
        # -----------------------------------------
        if self.employee_id and self.company_id:
            if self.employee.company_id != self.company_id:
                errors["employee"] = (
                    "The employee must belong to the selected company."
                )

        # -----------------------------------------
        # Work order and company validation
        # -----------------------------------------
        if self.work_order_id and self.company_id:
            if self.work_order.company_id != self.company_id:
                errors["work_order"] = (
                    "The work order must belong to the selected company."
                )

        # -----------------------------------------
        # Time validation
        # -----------------------------------------
        if self.start_time and self.end_time:

            if self.start_time >= self.end_time:
                errors["end_time"] = (
                    "End time must be after start time."
                )

        # -----------------------------------------
        # Hours validation
        # -----------------------------------------
        if self.regular_hours < 0:
            errors["regular_hours"] = (
                "Regular hours cannot be negative."
            )

        if self.overtime_hours < 0:
            errors["overtime_hours"] = (
                "Overtime hours cannot be negative."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.start_time:%Y-%m-%d %H:%M}"
        )