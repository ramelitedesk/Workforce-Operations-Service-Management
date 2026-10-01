from django.conf import settings
from django.db import models

from organizations.models import Company
from customers.models import Customer, CustomerLocation
from services.models import Service
from contracts.models import Contract, SLA


class TicketPriority(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class TicketStatus(models.TextChoices):
    NEW = "NEW", "New"
    ASSIGNED = "ASSIGNED", "Assigned"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    WAITING_CUSTOMER = "WAITING_CUSTOMER", "Waiting for Customer"
    WAITING_PARTS = "WAITING_PARTS", "Waiting for Parts"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"
    CANCELLED = "CANCELLED", "Cancelled"


class TicketSource(models.TextChoices):
    PHONE = "PHONE", "Phone"
    EMAIL = "EMAIL", "Email"
    PORTAL = "PORTAL", "Customer Portal"
    INTERNAL = "INTERNAL", "Internal"
    OTHER = "OTHER", "Other"


class Ticket(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    ticket_number = models.CharField(max_length=50)

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    location = models.ForeignKey(
        CustomerLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )

    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )

    sla = models.ForeignKey(
        SLA,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )

    title = models.CharField(max_length=250)

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
    )

    status = models.CharField(
        max_length=30,
        choices=TicketStatus.choices,
        default=TicketStatus.NEW,
    )

    source = models.CharField(
        max_length=20,
        choices=TicketSource.choices,
        default=TicketSource.PORTAL,
    )

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_tickets",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    due_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    resolution_notes = models.TextField(
        blank=True,
    )

    customer_feedback = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "ticket_number"],
                name="unique_ticket_number_per_company",
            )
        ]

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"