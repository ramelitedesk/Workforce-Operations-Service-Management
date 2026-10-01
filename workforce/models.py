from django.conf import settings
from django.db import models

from organizations.models import Company


class Department(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="departments",
    )

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_department_per_company",
            )
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class EmployeeEmploymentType(models.TextChoices):
    FULL_TIME = "FULL_TIME", "Full Time"
    PART_TIME = "PART_TIME", "Part Time"
    CONTRACT = "CONTRACT", "Contract"
    TEMPORARY = "TEMPORARY", "Temporary"
    FREELANCER = "FREELANCER", "Freelancer"


class EmployeeStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    ON_LEAVE = "ON_LEAVE", "On Leave"
    SUSPENDED = "SUSPENDED", "Suspended"
    TERMINATED = "TERMINATED", "Terminated"


class Employee(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employees",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
    )

    employee_id = models.CharField(
        max_length=50
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    designation = models.CharField(
        max_length=150,
        blank=True
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmployeeEmploymentType.choices,
        default=EmployeeEmploymentType.FULL_TIME,
    )

    joining_date = models.DateField(
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    alternate_email = models.EmailField(
        blank=True
    )

    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["company", "employee_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "employee_id"],
                name="unique_employee_id_per_company",
            )
        ]

    def __str__(self):
        if self.user:
            return f"{self.employee_id} - {self.user.get_full_name() or self.user.email}"

        return self.employee_id


class Team(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="teams",
    )

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_teams",
    )

    members = models.ManyToManyField(
        Employee,
        blank=True,
        related_name="teams",
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_team_per_company",
            )
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"