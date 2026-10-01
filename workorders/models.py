from django.conf import settings
from django.db import models

from organizations.models import Company
from customers.models import Customer, CustomerLocation
from services.models import Service
from tickets.models import Ticket
from workforce.models import Employee


class WorkOrderStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING = "PENDING", "Pending"
    ASSIGNED = "ASSIGNED", "Assigned"
    SCHEDULED = "SCHEDULED", "Scheduled"
    DISPATCHED = "DISPATCHED", "Dispatched"
    EN_ROUTE = "EN_ROUTE", "En Route"
    ON_SITE = "ON_SITE", "On Site"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    VERIFIED = "VERIFIED", "Verified"
    CLOSED = "CLOSED", "Closed"
    CANCELLED = "CANCELLED", "Cancelled"


class WorkOrderPriority(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class WorkOrder(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="work_orders",
    )

    work_order_number = models.CharField(
        max_length=50,
    )

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="work_orders",
    )

    location = models.ForeignKey(
        CustomerLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
    )

    title = models.CharField(
        max_length=250,
    )

    description = models.TextField(
        blank=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=WorkOrderPriority.choices,
        default=WorkOrderPriority.MEDIUM,
    )

    status = models.CharField(
        max_length=30,
        choices=WorkOrderStatus.choices,
        default=WorkOrderStatus.DRAFT,
    )

    assigned_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work_orders",
    )

    scheduled_start = models.DateTimeField(
        null=True,
        blank=True,
    )

    scheduled_end = models.DateTimeField(
        null=True,
        blank=True,
    )

    actual_start = models.DateTimeField(
        null=True,
        blank=True,
    )

    actual_end = models.DateTimeField(
        null=True,
        blank=True,
    )

    completion_notes = models.TextField(
        blank=True,
    )

    verification_notes = models.TextField(
        blank=True,
    )

    customer_approved = models.BooleanField(
        default=False,
    )

    customer_approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "work_order_number"],
                name="unique_work_order_number_per_company",
            )
        ]

    def __str__(self):
        return f"{self.work_order_number} - {self.title}"