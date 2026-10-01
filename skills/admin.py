from django.contrib import admin

from .models import (
    Skill,
    EmployeeSkill,
    Certification,
    EmployeeCertification,
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "company__name",
    )

    ordering = (
        "company",
        "name",
    )


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "skill",
        "proficiency",
        "years_of_experience",
        "created_at",
    )

    list_filter = (
        "skill",
        "proficiency",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
        "skill__name",
    )

    ordering = (
        "employee",
        "skill",
    )


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "issuing_authority",
        "validity_period_months",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company",
        "is_active",
        "issuing_authority",
    )

    search_fields = (
        "name",
        "description",
        "issuing_authority",
        "company__name",
    )

    ordering = (
        "company",
        "name",
    )


@admin.register(EmployeeCertification)
class EmployeeCertificationAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "certification",
        "certificate_number",
        "issue_date",
        "expiry_date",
        "created_at",
    )

    list_filter = (
        "certification",
        "issue_date",
        "expiry_date",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
        "certification__name",
        "certificate_number",
    )

    ordering = (
        "employee",
        "certification",
    )