from django.db import models

from organizations.models import Company
from customers.models import Customer
from services.models import Service


class ContractStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    SUSPENDED = "SUSPENDED", "Suspended"
    CANCELLED = "CANCELLED", "Cancelled"


class Contract(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="contracts",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="contracts",
    )

    contract_number = models.CharField(max_length=50)

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=ContractStatus.choices,
        default=ContractStatus.DRAFT,
    )

    contract_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )

    auto_renew = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company", "contract_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "contract_number"],
                name="unique_contract_number_per_company",
            )
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.name}"


class ContractService(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="contract_services",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="contract_services",
    )

    agreed_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    included_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["contract", "service"]

        constraints = [
            models.UniqueConstraint(
                fields=["contract", "service"],
                name="unique_service_per_contract",
            )
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.service.name}"


class SLA(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="slas",
    )

    name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    response_time_minutes = models.PositiveIntegerField(
        help_text="Maximum allowed time to respond to a ticket.",
    )

    resolution_time_minutes = models.PositiveIntegerField(
        help_text="Maximum allowed time to resolve a ticket.",
    )

    priority = models.CharField(
        max_length=20,
        choices=[
            ("LOW", "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH", "High"),
            ("CRITICAL", "Critical"),
        ],
        default="MEDIUM",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["contract", "priority", "name"]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.name}"