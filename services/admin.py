from django.contrib import admin

from .models import (
    Service,
    ServiceCategory,
    ServiceRequirement,
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):

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
            "Category Information",
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


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "company",
        "category",
        "duration_minutes",
        "base_price",
        "status",
        "requires_customer_approval",
    )

    list_filter = (
        "company",
        "category",
        "status",
        "requires_customer_approval",
    )

    search_fields = (
        "code",
        "name",
        "description",
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
            "Service Information",
            {
                "fields": (
                    "company",
                    "category",
                    "code",
                    "name",
                    "description",
                    "status",
                )
            },
        ),
        (
            "Service Configuration",
            {
                "fields": (
                    "duration_minutes",
                    "base_price",
                    "requires_customer_approval",
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


@admin.register(ServiceRequirement)
class ServiceRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "requirement_type",
        "skill",
        "certification",
        "minimum_proficiency",
        "is_required",
    )

    list_filter = (
        "requirement_type",
        "is_required",
    )

    search_fields = (
        "service__code",
        "service__name",
        "skill__name",
        "certification__name",
    )

    ordering = (
        "service",
        "requirement_type",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        (
            "Requirement",
            {
                "fields": (
                    "service",
                    "requirement_type",
                    "skill",
                    "certification",
                    "minimum_proficiency",
                    "is_required",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )