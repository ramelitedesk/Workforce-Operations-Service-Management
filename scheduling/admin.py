from django.contrib import admin

from .models import EmployeeAvailability, WorkSchedule

@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "work_order",
        "employee",
        "scheduled_start",
        "scheduled_end",
        "status",
        "company",
        "assigned_by",
    )

    list_filter = (
        "company",
        "status",
        "scheduled_start",
    )

    search_fields = (
        "work_order__work_order_number",
        "work_order__title",
        "employee__employee_id",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
    )

    ordering = (
        "scheduled_start",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Schedule",
            {
                "fields": (
                    "company",
                    "work_order",
                    "employee",
                    "scheduled_start",
                    "scheduled_end",
                    "status",
                )
            },
        ),
        (
            "Assignment",
            {
                "fields": (
                    "assigned_by",
                    "notes",
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

@admin.register(EmployeeAvailability)
class EmployeeAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "weekday",
        "start_time",
        "end_time",
        "is_available",
    )

    list_filter = (
        "weekday",
        "is_available",
        "employee__company",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )

    ordering = (
        "employee",
        "weekday",
        "start_time",
    )

    fieldsets = (
        (
            "Employee",
            {
                "fields": (
                    "employee",
                )
            },
        ),
        (
            "Availability",
            {
                "fields": (
                    "weekday",
                    "start_time",
                    "end_time",
                    "is_available",
                )
            },
        ),
    )