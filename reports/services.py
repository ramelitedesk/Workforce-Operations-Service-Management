from django.db.models import (
    F,
    Sum,
    DecimalField,
    ExpressionWrapper,
)
from django.utils import timezone

from customers.models import Customer
from tickets.models import Ticket
from workorders.models import WorkOrder
from workforce.models import Employee
from billing.models import Invoice
from inventory.models import Stock
from notifications.models import Notification
from attendance.models import Attendance


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

def get_dashboard_summary(company):
    """
    Generate dashboard KPIs for a specific company.
    """

    today = timezone.localdate()

    # -----------------------------------------------------
    # CUSTOMERS
    # -----------------------------------------------------

    total_customers = Customer.objects.filter(
        company=company
    ).count()

    # -----------------------------------------------------
    # TICKETS
    # -----------------------------------------------------

    open_tickets = Ticket.objects.filter(
        company=company
    ).exclude(
        status__in=[
            "CLOSED",
            "CANCELLED",
        ]
    ).count()

    closed_tickets = Ticket.objects.filter(
        company=company,
        status="CLOSED",
    ).count()

    # -----------------------------------------------------
    # WORK ORDERS
    # -----------------------------------------------------

    active_work_orders = WorkOrder.objects.filter(
        company=company
    ).exclude(
        status__in=[
            "COMPLETED",
            "VERIFIED",
            "CLOSED",
            "CANCELLED",
        ]
    ).count()

    completed_work_orders = WorkOrder.objects.filter(
        company=company,
        status__in=[
            "COMPLETED",
            "VERIFIED",
            "CLOSED",
        ],
    ).count()

    total_work_orders = WorkOrder.objects.filter(
        company=company
    ).count()

    # -----------------------------------------------------
    # WORKFORCE
    # -----------------------------------------------------

    active_employees = Employee.objects.filter(
        company=company,
        status="ACTIVE",
    ).count()

    # -----------------------------------------------------
    # ATTENDANCE
    # -----------------------------------------------------

    attendance_today = Attendance.objects.filter(
        company=company,
        attendance_date=today,
    ).count()

    # -----------------------------------------------------
    # BILLING
    # -----------------------------------------------------

    pending_invoices = Invoice.objects.filter(
        company=company,
        status__in=[
            "DRAFT",
            "ISSUED",
            "OVERDUE",
            "PARTIALLY_PAID",
        ],
    ).count()

    overdue_invoices = Invoice.objects.filter(
        company=company,
        status="OVERDUE",
    ).count()

    # Actual outstanding balance:
    # total amount - amount already paid
    total_outstanding = (
        Invoice.objects.filter(
            company=company,
            status__in=[
                "ISSUED",
                "OVERDUE",
                "PARTIALLY_PAID",
            ],
        )
        .aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("total_amount") - F("amount_paid"),
                    output_field=DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                )
            )
        )
        .get("total")
        or 0
    )

    # -----------------------------------------------------
    # INVENTORY
    # -----------------------------------------------------

    low_stock_products = 0

    stocks = Stock.objects.filter(
        company=company
    ).select_related("product")

    for stock in stocks:
        if (
            stock.available_quantity
            <= stock.product.reorder_level
        ):
            low_stock_products += 1

    # -----------------------------------------------------
    # NOTIFICATIONS
    # -----------------------------------------------------

    unread_notifications = Notification.objects.filter(
        recipient__company=company,
        status="UNREAD",
    ).count()

    # -----------------------------------------------------
    # WORK ORDER COMPLETION RATE
    # -----------------------------------------------------

    completion_rate = 0

    if total_work_orders > 0:
        completion_rate = round(
            (
                completed_work_orders
                / total_work_orders
            ) * 100
        )

    # -----------------------------------------------------
    # RETURN SUMMARY
    # -----------------------------------------------------

    return {
        "total_customers": total_customers,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "active_work_orders": active_work_orders,
        "completed_work_orders": completed_work_orders,
        "total_work_orders": total_work_orders,
        "active_employees": active_employees,
        "attendance_today": attendance_today,
        "pending_invoices": pending_invoices,
        "overdue_invoices": overdue_invoices,
        "total_outstanding": total_outstanding,
        "low_stock_products": low_stock_products,
        "unread_notifications": unread_notifications,
        "completion_rate": completion_rate,
    }


# =========================================================
# WORK ORDER CHART
# =========================================================

def get_work_order_chart_data(company):
    """
    Generate work order status distribution
    for the dashboard chart.
    """

    statuses = [
        "DRAFT",
        "PENDING",
        "ASSIGNED",
        "SCHEDULED",
        "DISPATCHED",
        "EN_ROUTE",
        "ON_SITE",
        "IN_PROGRESS",
        "COMPLETED",
        "VERIFIED",
        "CLOSED",
        "CANCELLED",
    ]

    labels = []
    values = []

    for status in statuses:
        count = WorkOrder.objects.filter(
            company=company,
            status=status,
        ).count()

        if count > 0:
            labels.append(
                status.replace("_", " ").title()
            )
            values.append(count)

    return {
        "labels": labels,
        "values": values,
    }


# =========================================================
# TICKET CHART
# =========================================================

def get_ticket_chart_data(company):
    """
    Generate ticket status distribution
    for the dashboard chart.
    """

    statuses = [
        "NEW",
        "ASSIGNED",
        "IN_PROGRESS",
        "WAITING_CUSTOMER",
        "WAITING_PARTS",
        "RESOLVED",
        "CLOSED",
        "CANCELLED",
    ]

    labels = []
    values = []

    for status in statuses:
        count = Ticket.objects.filter(
            company=company,
            status=status,
        ).count()

        if count > 0:
            labels.append(
                status.replace("_", " ").title()
            )
            values.append(count)

    return {
        "labels": labels,
        "values": values,
    }


# =========================================================
# RECENT WORK ORDERS
# =========================================================

def get_recent_work_orders(company):
    """
    Return the latest six work orders
    for the dashboard.
    """

    return (
        WorkOrder.objects.filter(
            company=company
        )
        .select_related(
            "customer",
            "assigned_employee",
        )
        .order_by("-created_at")[:6]
    )


# =========================================================
# OPERATIONAL ALERTS
# =========================================================

def get_operational_alerts(company):
    """
    Generate operational alerts based on
    current company dashboard data.
    """

    summary = get_dashboard_summary(company)

    alerts = []

    # -----------------------------------------------------
    # OPEN TICKETS
    # -----------------------------------------------------

    if summary["open_tickets"] > 0:
        alerts.append({
            "type": "warning",
            "title": "Open Tickets",
            "message": (
                f'{summary["open_tickets"]} ticket(s) '
                "require attention."
            ),
        })

    # -----------------------------------------------------
    # OVERDUE INVOICES
    # -----------------------------------------------------

    if summary["overdue_invoices"] > 0:
        alerts.append({
            "type": "danger",
            "title": "Overdue Invoices",
            "message": (
                f'{summary["overdue_invoices"]} invoice(s) '
                "are overdue."
            ),
        })

    # -----------------------------------------------------
    # LOW STOCK
    # -----------------------------------------------------

    if summary["low_stock_products"] > 0:
        alerts.append({
            "type": "warning",
            "title": "Low Stock",
            "message": (
                f'{summary["low_stock_products"]} product(s) '
                "are at or below reorder level."
            ),
        })

    # -----------------------------------------------------
    # UNREAD NOTIFICATIONS
    # -----------------------------------------------------

    if summary["unread_notifications"] > 0:
        alerts.append({
            "type": "info",
            "title": "Notifications",
            "message": (
                f'{summary["unread_notifications"]} '
                "unread notification(s)."
            ),
        })

    # -----------------------------------------------------
    # NO ALERTS
    # -----------------------------------------------------

    if not alerts:
        alerts.append({
            "type": "success",
            "title": "All Clear",
            "message": (
                "No operational alerts require attention."
            ),
        })

    return alerts


# =========================================================
# RECENT NOTIFICATIONS
# =========================================================

def get_recent_notifications(user):
    """
    Return the latest five notifications
    for the logged-in user.
    """

    return (
        Notification.objects.filter(
            recipient=user
        )
        .order_by("-created_at")[:5]
    )