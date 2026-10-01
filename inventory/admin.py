from django.contrib import admin

from .models import (
    Product,
    Warehouse,
    Stock,
    StockMovement,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "sku",
        "name",
        "company",
        "unit",
        "unit_cost",
        "minimum_stock",
        "reorder_level",
        "status",
    )

    list_filter = (
        "company",
        "status",
        "unit",
    )

    search_fields = (
        "sku",
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


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "company",
        "manager",
        "city",
        "is_active",
    )

    list_filter = (
        "company",
        "is_active",
        "city",
    )

    search_fields = (
        "code",
        "name",
        "city",
        "manager__employee_id",
        "manager__user__email",
    )

    ordering = (
        "company",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "warehouse",
        "company",
        "quantity",
        "reserved_quantity",
        "available_quantity_display",
        "updated_at",
    )

    list_filter = (
        "company",
        "warehouse",
        "product",
    )

    search_fields = (
        "product__sku",
        "product__name",
        "warehouse__code",
        "warehouse__name",
    )

    readonly_fields = (
        "updated_at",
        "available_quantity_display",
    )

    def available_quantity_display(self, obj):
        return obj.available_quantity

    available_quantity_display.short_description = "Available"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "warehouse",
        "movement_type",
        "quantity",
        "reference",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "company",
        "warehouse",
        "movement_type",
        "created_at",
    )

    search_fields = (
        "product__sku",
        "product__name",
        "warehouse__code",
        "reference",
        "notes",
        "performed_by__employee_id",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )