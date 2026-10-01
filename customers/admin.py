from django.contrib import admin

from .models import (
    Customer,
    CustomerContact,
    CustomerLocation,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "customer_code",
        "name",
        "company",
        "customer_type",
        "email",
        "phone",
        "status",
    )

    list_filter = (
        "company",
        "customer_type",
        "status",
    )

    search_fields = (
        "customer_code",
        "name",
        "legal_name",
        "email",
        "phone",
        "tax_number",
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
            "Customer Information",
            {
                "fields": (
                    "company",
                    "customer_code",
                    "customer_type",
                    "name",
                    "legal_name",
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
                    "tax_number",
                )
            },
        ),
        (
            "Additional Information",
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


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "customer",
        "designation",
        "email",
        "phone",
        "is_primary",
        "is_active",
    )

    list_filter = (
        "customer__company",
        "is_primary",
        "is_active",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "customer__name",
    )

    ordering = (
        "customer",
        "first_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Contact Information",
            {
                "fields": (
                    "customer",
                    "first_name",
                    "last_name",
                    "designation",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_primary",
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


@admin.register(CustomerLocation)
class CustomerLocationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "customer",
        "location_type",
        "city",
        "state",
        "country",
        "is_primary",
        "is_active",
    )

    list_filter = (
        "customer__company",
        "location_type",
        "country",
        "state",
        "is_primary",
        "is_active",
    )

    search_fields = (
        "name",
        "customer__name",
        "address",
        "city",
        "state",
        "postal_code",
    )

    ordering = (
        "customer",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Location Information",
            {
                "fields": (
                    "customer",
                    "name",
                    "location_type",
                    "is_primary",
                    "is_active",
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
            "Coordinates",
            {
                "fields": (
                    "latitude",
                    "longitude",
                )
            },
        ),
        (
            "Site Contact",
            {
                "fields": (
                    "contact_name",
                    "contact_phone",
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