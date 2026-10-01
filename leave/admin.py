from django.contrib import admin

from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "total_days_display",
        "status",
        "requested_by",
        "reviewed_by",
        "reviewed_at",
    )

    list_filter = (
        "company",
        "leave_type",
        "status",
        "start_date",
        "end_date",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
        "reason",
        "review_comments",
    )

    ordering = (
        "-start_date",
        "employee",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "total_days_display",
    )

    fieldsets = (
        (
            "Leave Request",
            {
                "fields": (
                    "company",
                    "employee",
                    "leave_type",
                    "start_date",
                    "end_date",
                    "total_days_display",
                    "reason",
                    "status",
                )
            },
        ),
        (
            "Request Information",
            {
                "fields": (
                    "requested_by",
                )
            },
        ),
        (
            "Review Information",
            {
                "fields": (
                    "reviewed_by",
                    "reviewed_at",
                    "review_comments",
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

    def total_days_display(self, obj):
        return obj.total_days

    total_days_display.short_description = "Total Days"