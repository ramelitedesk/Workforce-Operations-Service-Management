from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Company
from customers.models import Customer
from workorders.models import WorkOrder


class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ISSUED = "ISSUED", "Issued"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"


class Invoice(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="invoices",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="invoices",
    )

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )

    invoice_number = models.CharField(
        max_length=50,
    )

    invoice_date = models.DateField()

    due_date = models.DateField()

    status = models.CharField(
        max_length=30,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
    )

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    discount_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    amount_paid = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
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
        ordering = ["-invoice_date", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "invoice_number"],
                name="unique_invoice_number_per_company",
            )
        ]

    @property
    def balance_due(self):
        return max(
            Decimal("0"),
            self.total_amount - self.amount_paid,
        )

    def calculate_total(self):
        self.total_amount = (
            self.subtotal
            + self.tax_amount
            - self.discount_amount
        )

    def clean(self):
        errors = {}

        if self.customer_id and self.company_id:
            if self.customer.company_id != self.company_id:
                errors["customer"] = (
                    "The customer must belong "
                    "to the selected company."
                )

        if self.work_order_id and self.company_id:
            if self.work_order.company_id != self.company_id:
                errors["work_order"] = (
                    "The work order must belong "
                    "to the selected company."
                )

        if self.invoice_date and self.due_date:
            if self.due_date < self.invoice_date:
                errors["due_date"] = (
                    "Due date cannot be before invoice date."
                )

        if self.subtotal < 0:
            errors["subtotal"] = (
                "Subtotal cannot be negative."
            )

        if self.tax_amount < 0:
            errors["tax_amount"] = (
                "Tax amount cannot be negative."
            )

        if self.discount_amount < 0:
            errors["discount_amount"] = (
                "Discount cannot be negative."
            )

        if self.amount_paid < 0:
            errors["amount_paid"] = (
                "Amount paid cannot be negative."
            )

        self.calculate_total()

        if self.total_amount < 0:
            errors["total_amount"] = (
                "Total amount cannot be negative."
            )

        if self.amount_paid > self.total_amount:
            errors["amount_paid"] = (
                "Amount paid cannot exceed invoice total."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"


class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
    )

    description = models.CharField(
        max_length=250,
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
    )

    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    discount_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    @property
    def line_subtotal(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        taxable_amount = (
            self.line_subtotal - self.discount_amount
        )

        return (
            taxable_amount
            * self.tax_rate
            / Decimal("100")
        )

    @property
    def line_total(self):
        return (
            self.line_subtotal
            - self.discount_amount
            + self.tax_amount
        )

    def clean(self):
        errors = {}

        if self.quantity <= 0:
            errors["quantity"] = "Quantity must be greater than zero."

        if self.unit_price < 0:
            errors["unit_price"] = "Unit price cannot be negative."

        if self.tax_rate < 0:
            errors["tax_rate"] = "Tax rate cannot be negative."

        if self.discount_amount < 0:
            errors["discount_amount"] = "Discount cannot be negative."

        if self.discount_amount > self.line_subtotal:
           errors["discount_amount"] = (
                "Discount cannot exceed the line subtotal."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.description


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CARD = "CARD", "Card"
    UPI = "UPI", "UPI"
    CHEQUE = "CHEQUE", "Cheque"
    OTHER = "OTHER", "Other"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class Payment(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    reference_number = models.CharField(
        max_length=150,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def clean(self):
        errors = {}

        if self.amount <= 0:
            errors["amount"] = (
                "Payment amount must be greater than zero."
            )

        if self.invoice_id and self.company_id:
            if self.invoice.company_id != self.company_id:
                errors["invoice"] = (
                    "The invoice must belong "
                    "to the selected company."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.invoice.invoice_number} - "
            f"{self.amount}"
        )


class ExpenseStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PAID = "PAID", "Paid"


class Expense(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )

    description = models.CharField(
        max_length=250,
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    expense_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=ExpenseStatus.choices,
        default=ExpenseStatus.PENDING,
    )

    notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_expenses",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def clean(self):
        errors = {}

        if self.amount <= 0:
            errors["amount"] = (
                "Expense amount must be greater than zero."
            )

        if self.work_order_id and self.company_id:
            if self.work_order.company_id != self.company_id:
                errors["work_order"] = (
                    "The work order must belong "
                    "to the selected company."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.description} - {self.amount}"