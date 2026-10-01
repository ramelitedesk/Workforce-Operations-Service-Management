from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Company
from customers.models import Customer, CustomerLocation
from workforce.models import Employee


class AssetStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    IN_MAINTENANCE = "IN_MAINTENANCE", "In Maintenance"
    RETIRED = "RETIRED", "Retired"
    LOST = "LOST", "Lost"
    DAMAGED = "DAMAGED", "Damaged"


class AssetCategory(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="asset_categories",
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
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
        ordering = [
            "company",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "name",
                ],
                name="unique_asset_category_per_company",
            )
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Asset(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="assets",
    )

    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )

    location = models.ForeignKey(
        CustomerLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )

    assigned_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_assets",
    )

    asset_tag = models.CharField(
        max_length=100,
    )

    name = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    manufacturer = models.CharField(
        max_length=150,
        blank=True,
    )

    model_number = models.CharField(
        max_length=150,
        blank=True,
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
    )

    purchase_date = models.DateField(
        null=True,
        blank=True,
    )

    purchase_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )

    warranty_start_date = models.DateField(
        null=True,
        blank=True,
    )

    warranty_end_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=AssetStatus.choices,
        default=AssetStatus.ACTIVE,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "company",
            "asset_tag",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "asset_tag",
                ],
                name="unique_asset_tag_per_company",
            )
        ]

    def clean(self):

        errors = {}

        # -------------------------------------------------
        # Company / Category
        # -------------------------------------------------

        if self.category_id and self.company_id:

            if self.category.company_id != self.company_id:
                errors["category"] = (
                    "The asset category must belong "
                    "to the selected company."
                )

        # -------------------------------------------------
        # Company / Customer
        # -------------------------------------------------

        if self.customer_id and self.company_id:

            if self.customer.company_id != self.company_id:
                errors["customer"] = (
                    "The customer must belong "
                    "to the selected company."
                )

        # -------------------------------------------------
        # Company / Employee
        # -------------------------------------------------

        if self.assigned_employee_id and self.company_id:

            if (
                self.assigned_employee.company_id
                != self.company_id
            ):
                errors["assigned_employee"] = (
                    "The employee must belong "
                    "to the selected company."
                )

        # -------------------------------------------------
        # Company / Location
        # -------------------------------------------------

        if self.location_id and self.customer_id:

            if (
                self.location.customer_id
                != self.customer_id
            ):
                errors["location"] = (
                    "The location must belong "
                    "to the selected customer."
                )

        # -------------------------------------------------
        # Purchase date
        # -------------------------------------------------

        if (
            self.purchase_date
            and self.warranty_start_date
        ):

            if self.warranty_start_date < self.purchase_date:
                errors["warranty_start_date"] = (
                    "Warranty start date cannot be "
                    "before purchase date."
                )

        # -------------------------------------------------
        # Warranty dates
        # -------------------------------------------------

        if (
            self.warranty_start_date
            and self.warranty_end_date
        ):

            if self.warranty_end_date < self.warranty_start_date:
                errors["warranty_end_date"] = (
                    "Warranty end date must be after "
                    "warranty start date."
                )

        # -------------------------------------------------
        # Purchase price
        # -------------------------------------------------

        if self.purchase_price is not None:

            if self.purchase_price < 0:
                errors["purchase_price"] = (
                    "Purchase price cannot be negative."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def is_under_warranty(self):

        from django.utils import timezone

        today = timezone.localdate()

        if not self.warranty_start_date:
            return False

        if not self.warranty_end_date:
            return today >= self.warranty_start_date

        return (
            self.warranty_start_date
            <= today
            <= self.warranty_end_date
        )

    def __str__(self):
        return f"{self.asset_tag} - {self.name}"


class MaintenanceType(models.TextChoices):
    PREVENTIVE = "PREVENTIVE", "Preventive"
    CORRECTIVE = "CORRECTIVE", "Corrective"
    INSPECTION = "INSPECTION", "Inspection"
    CALIBRATION = "CALIBRATION", "Calibration"


class MaintenanceStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planned"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class AssetMaintenance(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="asset_maintenance_records",
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )

    maintenance_type = models.CharField(
        max_length=30,
        choices=MaintenanceType.choices,
        default=MaintenanceType.PREVENTIVE,
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    scheduled_date = models.DateField()

    completed_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PLANNED,
    )

    performed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_maintenance_performed",
    )

    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    findings = models.TextField(
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_asset_maintenance",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-scheduled_date",
        ]

    def clean(self):

        errors = {}

        # -------------------------------------------------
        # Company / Asset
        # -------------------------------------------------

        if self.asset_id and self.company_id:

            if self.asset.company_id != self.company_id:
                errors["asset"] = (
                    "The asset must belong "
                    "to the selected company."
                )

        # -------------------------------------------------
        # Company / Employee
        # -------------------------------------------------

        if self.performed_by_id and self.company_id:

            if (
                self.performed_by.company_id
                != self.company_id
            ):
                errors["performed_by"] = (
                    "The employee must belong "
                    "to the selected company."
                )

        # -------------------------------------------------
        # Maintenance dates
        # -------------------------------------------------

        if (
            self.completed_date
            and self.scheduled_date
        ):

            if self.completed_date < self.scheduled_date:
                errors["completed_date"] = (
                    "Completed date cannot be "
                    "before scheduled date."
                )

        # -------------------------------------------------
        # Cost
        # -------------------------------------------------

        if self.cost < 0:
            errors["cost"] = (
                "Maintenance cost cannot be negative."
            )

        # -------------------------------------------------
        # Completed status
        # -------------------------------------------------

        if self.status == MaintenanceStatus.COMPLETED:

            if not self.completed_date:
                errors["completed_date"] = (
                    "Completed date is required when "
                    "maintenance status is Completed."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.asset.asset_tag} - "
            f"{self.title}"
        )