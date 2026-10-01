from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "title",
        "company",
        "customer",
        "priority",
        "status",
        "assigned_to",
        "created_at",
        "due_at",
    )

    list_filter = (
        "company",
        "priority",
        "status",
        "source",
        "created_at",
    )

    search_fields = (
        "ticket_number",
        "title",
        "description",
        "customer__name",
        "assigned_to__email",
        "assigned_to__first_name",
        "assigned_to__last_name",
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
            "Ticket Information",
            {
                "fields": (
                    "company",
                    "ticket_number",
                    "title",
                    "description",
                    "source",
                )
            },
        ),
        (
            "Customer & Service",
            {
                "fields": (
                    "customer",
                    "location",
                    "contract",
                    "service",
                    "sla",
                )
            },
        ),
        (
            "Priority & Assignment",
            {
                "fields": (
                    "priority",
                    "status",
                    "reported_by",
                    "assigned_to",
                    "due_at",
                )
            },
        ),
        (
            "Resolution",
            {
                "fields": (
                    "resolved_at",
                    "closed_at",
                    "resolution_notes",
                    "customer_feedback",
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