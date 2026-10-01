from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "recipient",
        "title",
        "notification_type",
        "channel",
        "priority",
        "status",
        "created_at",
        "read_at",
    )

    list_filter = (
        "notification_type",
        "channel",
        "priority",
        "status",
        "created_at",
    )

    search_fields = (
        "recipient__email",
        "recipient__first_name",
        "recipient__last_name",
        "title",
        "message",
        "object_type",
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
            "Notification",
            {
                "fields": (
                    "recipient",
                    "notification_type",
                    "channel",
                    "priority",
                    "title",
                    "message",
                )
            },
        ),
        (
            "Related Object",
            {
                "fields": (
                    "object_type",
                    "object_id",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "read_at",
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