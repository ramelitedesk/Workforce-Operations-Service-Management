from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Invoice,
    InvoiceStatus,
    Payment,
    PaymentStatus,
)


@transaction.atomic
def recalculate_invoice(invoice):
    """
    Recalculate invoice totals from InvoiceItems.
    """

    items = invoice.items.all()

    subtotal = Decimal("0")
    tax_amount = Decimal("0")
    discount_amount = Decimal("0")

    for item in items:
        subtotal += item.line_subtotal
        tax_amount += item.tax_amount
        discount_amount += item.discount_amount

    total_amount = subtotal + tax_amount - discount_amount

    if total_amount < 0:
        raise ValidationError(
            "Invoice total cannot be negative."
        )

    invoice.subtotal = subtotal
    invoice.tax_amount = tax_amount
    invoice.discount_amount = discount_amount
    invoice.total_amount = total_amount

    if invoice.amount_paid > total_amount:
        raise ValidationError(
            "Existing payments cannot exceed the recalculated invoice total."
        )

    invoice.save(
        update_fields=[
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "updated_at",
        ]
    )

    update_invoice_status(invoice)

    return invoice


@transaction.atomic
def record_payment(
    *,
    invoice,
    amount,
    payment_date=None,
    payment_method="BANK_TRANSFER",
    reference_number="",
    notes="",
    recorded_by=None,
):
    """
    Record a payment and automatically update invoice balance/status.
    """

    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValidationError(
            "Payment amount must be greater than zero."
        )

    invoice = Invoice.objects.select_for_update().get(
        pk=invoice.pk
    )

    if invoice.status == InvoiceStatus.CANCELLED:
        raise ValidationError(
            "Payments cannot be recorded against a cancelled invoice."
        )

    balance_due = invoice.balance_due

    if amount > balance_due:
        raise ValidationError(
            f"Payment cannot exceed the remaining balance of {balance_due}."
        )

    payment = Payment.objects.create(
        company=invoice.company,
        invoice=invoice,
        amount=amount,
        payment_date=payment_date or timezone.localdate(),
        payment_method=payment_method,
        status=PaymentStatus.COMPLETED,
        reference_number=reference_number,
        notes=notes,
        recorded_by=recorded_by,
    )

    invoice.amount_paid += amount

    update_invoice_status(invoice)

    invoice.save(
        update_fields=[
            "amount_paid",
            "status",
            "updated_at",
        ]
    )

    return payment, invoice


def update_invoice_status(invoice):
    """
    Determine invoice status from amount paid and due date.
    """

    if invoice.status == InvoiceStatus.CANCELLED:
        return invoice.status

    if invoice.amount_paid >= invoice.total_amount:
        invoice.status = InvoiceStatus.PAID

    elif invoice.amount_paid > 0:
        invoice.status = InvoiceStatus.PARTIALLY_PAID

    elif (
        invoice.due_date
        and invoice.due_date < timezone.localdate()
        and invoice.total_amount > 0
    ):
        invoice.status = InvoiceStatus.OVERDUE

    elif invoice.status != InvoiceStatus.DRAFT:
        invoice.status = InvoiceStatus.ISSUED

    return invoice.status