from django.contrib import admin

from .models import (
    AssetCategory,
    Asset,
    AssetMaintenance,
)


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
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
            "Category",
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


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    list_display = (
        "asset_tag",
        "name",
        "category",
        "company",
        "customer",
        "assigned_employee",
        "status",
        "warranty_status",
    )

    list_filter = (
        "company",
        "category",
        "status",
        "purchase_date",
        "warranty_end_date",
    )

    search_fields = (
        "asset_tag",
        "name",
        "serial_number",
        "manufacturer",
        "model_number",
        "customer__name",
        "assigned_employee__employee_id",
        "assigned_employee__user__email",
    )

    ordering = (
        "company",
        "asset_tag",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "warranty_status",
    )

    fieldsets = (
        (
            "Asset Information",
            {
                "fields": (
                    "company",
                    "category",
                    "asset_tag",
                    "name",
                    "description",
                    "status",
                )
            },
        ),
        (
            "Ownership & Assignment",
            {
                "fields": (
                    "customer",
                    "location",
                    "assigned_employee",
                )
            },
        ),
        (
            "Identification",
            {
                "fields": (
                    "manufacturer",
                    "model_number",
                    "serial_number",
                )
            },
        ),
        (
            "Purchase & Warranty",
            {
                "fields": (
                    "purchase_date",
                    "purchase_price",
                    "warranty_start_date",
                    "warranty_end_date",
                    "warranty_status",
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

    def warranty_status(self, obj):

        if obj.is_under_warranty:
            return "Under Warranty"

        return "Warranty Expired / Not Available"

    warranty_status.short_description = "Warranty"


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):

    list_display = (
        "asset",
        "maintenance_type",
        "title",
        "scheduled_date",
        "completed_date",
        "status",
        "performed_by",
        "cost",
    )

    list_filter = (
        "company",
        "maintenance_type",
        "status",
        "scheduled_date",
        "completed_date",
    )

    search_fields = (
        "asset__asset_tag",
        "asset__name",
        "title",
        "description",
        "performed_by__employee_id",
        "performed_by__user__email",
    )

    ordering = (
        "-scheduled_date",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Maintenance",
            {
                "fields": (
                    "company",
                    "asset",
                    "maintenance_type",
                    "title",
                    "description",
                    "status",
                )
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "scheduled_date",
                    "completed_date",
                )
            },
        ),
        (
            "Execution",
            {
                "fields": (
                    "performed_by",
                    "cost",
                    "findings",
                    "notes",
                )
            },
        ),
        (
            "Created By",
            {
                "fields": (
                    "created_by",
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