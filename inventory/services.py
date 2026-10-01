from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    Product,
    Stock,
    StockMovement,
    StockMovementType,
    Warehouse,
)


@transaction.atomic
def record_stock_movement(
    *,
    company,
    product,
    warehouse,
    movement_type,
    quantity,
    performed_by=None,
    reference="",
    notes="",
):
    """
    Create a stock movement and update the corresponding Stock record
    atomically.
    """

    quantity = Decimal(str(quantity))

    if quantity <= 0:
        raise ValidationError("Movement quantity must be greater than zero.")

    if product.company_id != company.id:
        raise ValidationError(
            "The product must belong to the selected company."
        )

    if warehouse.company_id != company.id:
        raise ValidationError(
            "The warehouse must belong to the selected company."
        )

    if performed_by and performed_by.company_id != company.id:
        raise ValidationError(
            "The employee must belong to the selected company."
        )

    stock, _ = Stock.objects.select_for_update().get_or_create(
        company=company,
        warehouse=warehouse,
        product=product,
        defaults={
            "quantity": Decimal("0"),
            "reserved_quantity": Decimal("0"),
        },
    )

    current_quantity = stock.quantity

    if movement_type in [
        StockMovementType.RECEIPT,
        StockMovementType.RETURN,
    ]:
        stock.quantity += quantity

    elif movement_type == StockMovementType.ISSUE:
        if quantity > stock.available_quantity:
            raise ValidationError(
                "Insufficient available stock for this issue."
            )

        stock.quantity -= quantity

    elif movement_type == StockMovementType.ADJUSTMENT:
        stock.quantity = quantity

    elif movement_type == StockMovementType.TRANSFER:
        raise ValidationError(
            "Use the transfer_stock() service for stock transfers."
        )

    else:
        raise ValidationError(
            "Unsupported stock movement type."
        )

    if stock.quantity < 0:
        raise ValidationError(
            "Stock quantity cannot become negative."
        )

    if stock.reserved_quantity > stock.quantity:
        raise ValidationError(
            "Stock quantity cannot be lower than reserved quantity."
        )

    stock.full_clean()
    stock.save()

    movement = StockMovement.objects.create(
        company=company,
        product=product,
        warehouse=warehouse,
        movement_type=movement_type,
        quantity=quantity,
        reference=reference,
        notes=notes,
        performed_by=performed_by,
    )

    return movement, stock


@transaction.atomic
def transfer_stock(
    *,
    company,
    product,
    source_warehouse,
    destination_warehouse,
    quantity,
    performed_by=None,
    reference="",
    notes="",
):
    """
    Transfer stock from one warehouse to another atomically.
    """

    quantity = Decimal(str(quantity))

    if quantity <= 0:
        raise ValidationError(
            "Transfer quantity must be greater than zero."
        )

    if source_warehouse.id == destination_warehouse.id:
        raise ValidationError(
            "Source and destination warehouses must be different."
        )

    if source_warehouse.company_id != company.id:
        raise ValidationError(
            "The source warehouse must belong to the selected company."
        )

    if destination_warehouse.company_id != company.id:
        raise ValidationError(
            "The destination warehouse must belong to the selected company."
        )

    if product.company_id != company.id:
        raise ValidationError(
            "The product must belong to the selected company."
        )

    source_stock = (
        Stock.objects
        .select_for_update()
        .filter(
            company=company,
            warehouse=source_warehouse,
            product=product,
        )
        .first()
    )

    if not source_stock:
        raise ValidationError(
            "No stock record exists in the source warehouse."
        )

    if quantity > source_stock.available_quantity:
        raise ValidationError(
            "Insufficient available stock in the source warehouse."
        )

    destination_stock, _ = Stock.objects.select_for_update().get_or_create(
        company=company,
        warehouse=destination_warehouse,
        product=product,
        defaults={
            "quantity": Decimal("0"),
            "reserved_quantity": Decimal("0"),
        },
    )

    source_stock.quantity -= quantity

    if source_stock.quantity < source_stock.reserved_quantity:
        raise ValidationError(
            "Transfer would reduce source stock below its reserved quantity."
        )

    source_stock.full_clean()
    source_stock.save()

    destination_stock.quantity += quantity
    destination_stock.full_clean()
    destination_stock.save()

    transfer_reference = reference or "STOCK-TRANSFER"

    outbound_movement = StockMovement.objects.create(
        company=company,
        product=product,
        warehouse=source_warehouse,
        movement_type=StockMovementType.TRANSFER,
        quantity=quantity,
        reference=transfer_reference,
        notes=notes,
        performed_by=performed_by,
    )

    inbound_movement = StockMovement.objects.create(
        company=company,
        product=product,
        warehouse=destination_warehouse,
        movement_type=StockMovementType.TRANSFER,
        quantity=quantity,
        reference=transfer_reference,
        notes=notes,
        performed_by=performed_by,
    )

    return (
        outbound_movement,
        inbound_movement,
        source_stock,
        destination_stock,
    )