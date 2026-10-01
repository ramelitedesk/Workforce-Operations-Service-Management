from django.contrib import admin

from .models import WorkOrder


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "work_order_number",
        "title",
        "company",
        "customer",
        "assigned_employee",
        "priority",
        "status",
        "scheduled_start",
        "scheduled_end",
        "customer_approved",
    )

    list_filter = (
        "company",
        "priority",
        "status",
        "customer_approved",
    )

    search_fields = (
        "work_order_number",
        "title",
        "description",
        "customer__name",
        "ticket__ticket_number",
        "assigned_employee__employee_id",
        "assigned_employee__user__first_name",
        "assigned_employee__user__last_name",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Work Order Information",
            {
                "fields": (
                    "company",
                    "work_order_number",
                    "ticket",
                    "title",
                    "description",
                )
            },
        ),
        (
            "Customer & Service",
            {
                "fields": (
                    "customer",
                    "location",
                    "service",
                )
            },
        ),
        (
            "Priority & Status",
            {
                "fields": (
                    "priority",
                    "status",
                )
            },
        ),
        (
            "Assignment",
            {
                "fields": (
                    "assigned_employee",
                    "assigned_by",
                )
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "scheduled_start",
                    "scheduled_end",
                )
            },
        ),
        (
            "Execution",
            {
                "fields": (
                    "actual_start",
                    "actual_end",
                    "completion_notes",
                )
            },
        ),
        (
            "Customer Verification",
            {
                "fields": (
                    "verification_notes",
                    "customer_approved",
                    "customer_approved_at",
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