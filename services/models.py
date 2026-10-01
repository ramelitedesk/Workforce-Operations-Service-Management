from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Company
from skills.models import Skill, Certification


class ServiceCategory(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="service_categories",
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_service_category_per_company",
            )
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class ServiceStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class Service(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="services",
    )

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
    )

    code = models.CharField(
        max_length=50,
    )

    name = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    duration_minutes = models.PositiveIntegerField(
        default=60,
    )

    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=ServiceStatus.choices,
        default=ServiceStatus.ACTIVE,
    )

    requires_customer_approval = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_service_code_per_company",
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class ServiceRequirement(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="requirements",
    )

    requirement_type = models.CharField(
        max_length=30,
        choices=[
            ("SKILL", "Skill"),
            ("CERTIFICATION", "Certification"),
        ],
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="service_requirements",
    )

    certification = models.ForeignKey(
        Certification,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="service_requirements",
    )

    minimum_proficiency = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Required proficiency level from 1 to 5. Used for skills.",
    )

    is_required = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            "service",
            "requirement_type",
        ]

    def clean(self):
        errors = {}

        if self.requirement_type == "SKILL":
            if not self.skill:
                errors["skill"] = (
                    "A skill is required when requirement type is Skill."
                )

            if self.certification:
                errors["certification"] = (
                    "Certification must be empty when requirement type is Skill."
                )

        elif self.requirement_type == "CERTIFICATION":
            if not self.certification:
                errors["certification"] = (
                    "A certification is required when requirement type is Certification."
                )

            if self.skill:
                errors["skill"] = (
                    "Skill must be empty when requirement type is Certification."
                )

            if self.minimum_proficiency is not None:
                errors["minimum_proficiency"] = (
                    "Minimum proficiency applies only to skill requirements."
                )

        if self.minimum_proficiency is not None:
            if not 1 <= self.minimum_proficiency <= 5:
                errors["minimum_proficiency"] = (
                    "Minimum proficiency must be between 1 and 5."
                )

        if errors:
            raise ValidationError(errors)

        # Tenant/company consistency checks
        if self.service_id:
            if self.skill_id and self.skill.company_id != self.service.company_id:
                errors["skill"] = (
                    "The selected skill must belong to the same company as the service."
                )

            if (
                self.certification_id
                and self.certification.company_id != self.service.company_id
            ):
                errors["certification"] = (
                    "The selected certification must belong to the same company as the service."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        if self.requirement_type == "SKILL" and self.skill:
            return f"{self.service.code} - Skill: {self.skill.name}"

        if self.requirement_type == "CERTIFICATION" and self.certification:
            return (
                f"{self.service.code} - "
                f"Certification: {self.certification.name}"
            )

        return f"{self.service.code} - Requirement"