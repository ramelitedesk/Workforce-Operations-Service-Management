from django.contrib import admin

from .models import WorkOrderAssignment


@admin.register(WorkOrderAssignment)
class WorkOrderAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "work_order",
        "employee",
        "company",
        "status",
        "assigned_by",
        "assigned_at",
    )

    list_filter = (
        "company",
        "status",
        "assigned_at",
    )

    search_fields = (
        "work_order__work_order_number",
        "work_order__title",
        "employee__employee_id",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
        "assignment_reason",
        "notes",
    )

    ordering = (
        "-assigned_at",
    )

    readonly_fields = (
        "assigned_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Assignment",
            {
                "fields": (
                    "company",
                    "work_order",
                    "employee",
                    "status",
                )
            },
        ),
        (
            "Assignment Details",
            {
                "fields": (
                    "assigned_by",
                    "assignment_reason",
                    "notes",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "assigned_at",
                    "updated_at",
                )
            },
        ),
    )