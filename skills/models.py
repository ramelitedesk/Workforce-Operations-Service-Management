from django.db import models

from organizations.models import Company
from workforce.models import Employee


class ProficiencyLevel(models.IntegerChoices):
    BEGINNER = 1, "Beginner"
    INTERMEDIATE = 2, "Intermediate"
    ADVANCED = 3, "Advanced"
    EXPERT = 4, "Expert"
    MASTER = 5, "Master"


class Skill(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_skill_per_company",
            )
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="employees",
    )
    proficiency = models.PositiveSmallIntegerField(
        choices=ProficiencyLevel.choices,
        default=ProficiencyLevel.BEGINNER,
    )
    years_of_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee", "skill"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "skill"],
                name="unique_skill_per_employee",
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.skill.name} - "
            f"{self.get_proficiency_display()}"
        )


class Certification(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="certifications",
    )
    name = models.CharField(max_length=200)
    issuing_authority = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    validity_period_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional validity period in months.",
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_certification_per_company",
            )
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class EmployeeCertification(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="certifications",
    )
    certification = models.ForeignKey(
        Certification,
        on_delete=models.CASCADE,
        related_name="employees",
    )
    certificate_number = models.CharField(
        max_length=150,
        blank=True,
    )
    issue_date = models.DateField()
    expiry_date = models.DateField(
        null=True,
        blank=True,
    )
    issuing_authority = models.CharField(
        max_length=200,
        blank=True,
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee", "certification"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "certification",
                    "certificate_number",
                ],
                name="unique_employee_certification",
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.certification.name}"
        )