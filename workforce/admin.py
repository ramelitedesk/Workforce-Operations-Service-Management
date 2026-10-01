from django.contrib import admin

from .models import Department, Employee, Team


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "company__name",
    )

    ordering = (
        "company",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Department Information",
            {
                "fields": (
                    "company",
                    "name",
                    "description",
                    "is_active",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "user",
        "company",
        "department",
        "designation",
        "employment_type",
        "status",
        "joining_date",
    )

    list_filter = (
        "company",
        "department",
        "employment_type",
        "status",
    )

    search_fields = (
        "employee_id",
        "user__email",
        "user__first_name",
        "user__last_name",
        "designation",
        "phone",
    )

    ordering = (
        "company",
        "employee_id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Employee Information",
            {
                "fields": (
                    "company",
                    "employee_id",
                    "user",
                    "designation",
                    "department",
                    "manager",
                )
            },
        ),
        (
            "Employment",
            {
                "fields": (
                    "employment_type",
                    "joining_date",
                    "status",
                    "hourly_rate",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "phone",
                    "alternate_email",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "manager",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "company__name",
        "manager__employee_id",
        "manager__user__email",
    )

    filter_horizontal = (
        "members",
    )

    ordering = (
        "company",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Team Information",
            {
                "fields": (
                    "company",
                    "name",
                    "description",
                    "manager",
                    "members",
                    "is_active",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )