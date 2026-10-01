from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "legal_name",
        "email",
        "phone",
        "city",
        "country",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "country",
        "state",
    )

    search_fields = (
        "name",
        "legal_name",
        "registration_number",
        "tax_number",
        "email",
        "phone",
        "city",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Company Information",
            {
                "fields": (
                    "name",
                    "legal_name",
                    "registration_number",
                    "tax_number",
                    "status",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Address",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "country",
                    "postal_code",
                )
            },
        ),
        (
            "Business Settings",
            {
                "fields": (
                    "timezone",
                    "currency",
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