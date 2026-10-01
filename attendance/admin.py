from django.contrib import admin

from .models import Attendance, TimeEntry


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "attendance_date",
        "employee",
        "company",
        "status",
        "check_in",
        "check_out",
    )

    list_filter = (
        "company",
        "status",
        "attendance_date",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
    )

    ordering = (
        "-attendance_date",
        "employee",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Attendance",
            {
                "fields": (
                    "company",
                    "employee",
                    "attendance_date",
                    "status",
                    "check_in",
                    "check_out",
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


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "work_order",
        "start_time",
        "end_time",
        "regular_hours",
        "overtime_hours",
        "billable",
    )

    list_filter = (
        "company",
        "billable",
        "start_time",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__email",
        "work_order__work_order_number",
        "work_order__title",
    )

    ordering = (
        "-start_time",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Time Entry",
            {
                "fields": (
                    "company",
                    "employee",
                    "work_order",
                    "start_time",
                    "end_time",
                    "description",
                )
            },
        ),
        (
            "Hours",
            {
                "fields": (
                    "regular_hours",
                    "overtime_hours",
                    "billable",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": (
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