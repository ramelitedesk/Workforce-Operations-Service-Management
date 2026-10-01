from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Company
from workforce.models import Employee


class ProductStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class Product(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="inventory_products",
    )

    sku = models.CharField(
        max_length=100,
    )

    name = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    unit = models.CharField(
        max_length=30,
        default="PCS",
    )

    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.ACTIVE,
    )

    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    reorder_level = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["company", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "sku"],
                name="unique_product_sku_per_company",
            )
        ]

    def clean(self):
        errors = {}

        if self.minimum_stock < 0:
            errors["minimum_stock"] = (
                "Minimum stock cannot be negative."
            )

        if self.reorder_level < 0:
            errors["reorder_level"] = (
                "Reorder level cannot be negative."
            )

        if self.unit_cost < 0:
            errors["unit_cost"] = (
                "Unit cost cannot be negative."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Warehouse(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="warehouses",
    )

    name = models.CharField(
        max_length=150,
    )

    code = models.CharField(
        max_length=50,
    )

    address = models.TextField(
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        default="India",
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_warehouses",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["company", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_warehouse_code_per_company",
            )
        ]

    def clean(self):
        if self.manager_id and self.company_id:
            if self.manager.company_id != self.company_id:
                raise ValidationError({
                    "manager": (
                        "The warehouse manager must belong "
                        "to the selected company."
                    )
                })

    def __str__(self):
        return f"{self.code} - {self.name}"


class Stock(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="stock_records",
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stock_records",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_records",
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    reserved_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["warehouse", "product"]

        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product"],
                name="unique_product_stock_per_warehouse",
            )
        ]

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    def clean(self):
        errors = {}

        if self.warehouse_id and self.company_id:
            if self.warehouse.company_id != self.company_id:
                errors["warehouse"] = (
                    "The warehouse must belong "
                    "to the selected company."
                )

        if self.product_id and self.company_id:
            if self.product.company_id != self.company_id:
                errors["product"] = (
                    "The product must belong "
                    "to the selected company."
                )

        if self.quantity < 0:
            errors["quantity"] = (
                "Stock quantity cannot be negative."
            )

        if self.reserved_quantity < 0:
            errors["reserved_quantity"] = (
                "Reserved quantity cannot be negative."
            )

        if self.reserved_quantity > self.quantity:
            errors["reserved_quantity"] = (
                "Reserved quantity cannot exceed stock quantity."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.product.sku} - "
            f"{self.warehouse.code} - "
            f"{self.quantity}"
        )


class StockMovementType(models.TextChoices):
    RECEIPT = "RECEIPT", "Receipt"
    ISSUE = "ISSUE", "Issue"
    TRANSFER = "TRANSFER", "Transfer"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"
    RETURN = "RETURN", "Return"


class StockMovement(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=StockMovementType.choices,
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    reference = models.CharField(
        max_length=150,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    performed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_performed",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        errors = {}

        if self.quantity <= 0:
            errors["quantity"] = (
                "Movement quantity must be greater than zero."
            )

        if self.company_id and self.product_id:
            if self.product.company_id != self.company_id:
                errors["product"] = (
                    "The product must belong "
                    "to the selected company."
                )

        if self.company_id and self.warehouse_id:
            if self.warehouse.company_id != self.company_id:
                errors["warehouse"] = (
                    "The warehouse must belong "
                    "to the selected company."
                )

        if self.performed_by_id and self.company_id:
            if self.performed_by.company_id != self.company_id:
                errors["performed_by"] = (
                    "The employee must belong "
                    "to the selected company."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.product.sku} - "
            f"{self.get_movement_type_display()} - "
            f"{self.quantity}"
        )