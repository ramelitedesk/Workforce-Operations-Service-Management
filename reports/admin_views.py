from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .services import (
    get_dashboard_summary,
    get_work_order_chart_data,
    get_ticket_chart_data,
    get_recent_work_orders,
)


@staff_member_required
def reports_dashboard(request):

    user = request.user

    company = getattr(
        user,
        "company",
        None,
    )

    # ---------------------------------------------------------
    # DEFAULT DATA
    # ---------------------------------------------------------

    context = {
        "summary": {
            "total_customers": 0,
            "open_tickets": 0,
            "closed_tickets": 0,
            "active_work_orders": 0,
            "completed_work_orders": 0,
            "total_work_orders": 0,
            "active_employees": 0,
            "attendance_today": 0,
            "pending_invoices": 0,
            "overdue_invoices": 0,
            "total_outstanding": 0,
            "low_stock_products": 0,
            "unread_notifications": 0,
            "completion_rate": 0,
        },

        "work_order_chart": {
            "labels": [],
            "values": [],
        },

        "ticket_chart": {
            "labels": [],
            "values": [],
        },

        "recent_work_orders": [],

        "user": user,

        "company": company,
    }

    # ---------------------------------------------------------
    # COMPANY REPORT DATA
    # ---------------------------------------------------------

    if company:

        context["summary"] = get_dashboard_summary(
            company
        )

        context["work_order_chart"] = (
            get_work_order_chart_data(company)
        )

        context["ticket_chart"] = (
            get_ticket_chart_data(company)
        )

        context["recent_work_orders"] = (
            get_recent_work_orders(company)
        )

    # ---------------------------------------------------------
    # DJANGO ADMIN CONTEXT
    # ---------------------------------------------------------

    context.update(
        admin.site.each_context(request)
    )

    context["title"] = "Reports Dashboard"

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------

    return render(
        request,
        "admin/reports/dashboard.html",
        context,
    )