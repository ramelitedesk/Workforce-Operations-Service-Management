from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


from organizations.models import Company
from workforce.models import Employee


class LeaveType(models.TextChoices):
    CASUAL = "CASUAL", "Casual Leave"
    SICK = "SICK", "Sick Leave"
    ANNUAL = "ANNUAL", "Annual Leave"
    UNPAID = "UNPAID", "Unpaid Leave"
    MATERNITY = "MATERNITY", "Maternity Leave"
    PATERNITY = "PATERNITY", "Paternity Leave"
    OTHER = "OTHER", "Other"


class LeaveStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"


class LeaveRequest(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        default=LeaveType.CASUAL,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING,
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_leave_requests",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leave_requests",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    review_comments = models.TextField(
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
            "-start_date",
            "employee",
        ]

    def clean(self):
        errors = {}

        # -------------------------------------------------
        # Company / Employee validation
        # -------------------------------------------------

        if self.employee_id and self.company_id:
            if self.employee.company_id != self.company_id:
                errors["employee"] = (
                    "The employee must belong to the selected company."
                )

        # -------------------------------------------------
        # Date validation
        # -------------------------------------------------

        if self.start_date and self.end_date:

            if self.end_date < self.start_date:
                errors["end_date"] = (
                    "End date must be on or after the start date."
                )

        # -------------------------------------------------
        # Employee status validation
        # -------------------------------------------------

        if self.employee_id:

            if self.employee.status == "TERMINATED":
                errors["employee"] = (
                    "Terminated employees cannot request leave."
                )

        # -------------------------------------------------
        # Overlapping leave validation
        # -------------------------------------------------

        if (
            self.employee_id
            and self.start_date
            and self.end_date
        ):

            overlapping_requests = LeaveRequest.objects.filter(
                employee=self.employee,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )

            if self.pk:
                overlapping_requests = overlapping_requests.exclude(
                    pk=self.pk
                )

            # Prevent overlap with active leave requests.
            overlapping_requests = overlapping_requests.filter(
                status__in=[
                    LeaveStatus.PENDING,
                    LeaveStatus.APPROVED,
                ]
            )

            if overlapping_requests.exists():

                errors["start_date"] = (
                    "This employee already has an overlapping "
                    "pending or approved leave request."
                )

        # -------------------------------------------------
        # Review validation
        # -------------------------------------------------

        if self.status in [
            LeaveStatus.APPROVED,
            LeaveStatus.REJECTED,
        ]:

            if not self.reviewed_by_id:
                errors["reviewed_by"] = (
                    "A reviewer is required when leave is "
                    "approved or rejected."
                )

            if not self.reviewed_at:
                errors["reviewed_at"] = (
                    "Review date/time is required when leave "
                    "is approved or rejected."
                )

        # -------------------------------------------------
        # Pending validation
        # -------------------------------------------------

        if self.status == LeaveStatus.PENDING:

            if self.reviewed_at:
                errors["reviewed_at"] = (
                    "Pending leave should not have a review date."
                )

        # -------------------------------------------------
        # Requested-by company validation
        # -------------------------------------------------

        if self.requested_by_id and self.company_id:

            if (
                self.requested_by.company_id
                and self.requested_by.company_id != self.company_id
            ):
                errors["requested_by"] = (
                    "The requester must belong to the selected company."
                )

        # -------------------------------------------------
        # Reviewed-by company validation
        # -------------------------------------------------

        if self.reviewed_by_id and self.company_id:

            if (
                self.reviewed_by.company_id
                and self.reviewed_by.company_id != self.company_id
            ):
                errors["reviewed_by"] = (
                    "The reviewer must belong to the selected company."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def total_days(self):
        """
        Return the inclusive number of leave days.
        """
        if not self.start_date or not self.end_date:
            return 0

        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.get_leave_type_display()} - "
            f"{self.start_date} to {self.end_date}"
        )