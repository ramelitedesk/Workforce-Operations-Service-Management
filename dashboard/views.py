from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from reports.services import (
    get_dashboard_summary,
    get_work_order_chart_data,
    get_ticket_chart_data,
    get_recent_work_orders,
    get_recent_notifications,
    get_operational_alerts,
)


@login_required
def dashboard(request):
    user = request.user
    company = getattr(user, "company", None)

    context = {
        "user": user,

        "summary": {},

        "work_order_chart": {
            "labels": [],
            "values": [],
        },

        "ticket_chart": {
            "labels": [],
            "values": [],
        },

        "recent_work_orders": [],

        "recent_notifications": [],

        "operational_alerts": [],
    }

    if company:
        context["summary"] = get_dashboard_summary(company)

        context["work_order_chart"] = (
            get_work_order_chart_data(company)
        )

        context["ticket_chart"] = (
            get_ticket_chart_data(company)
        )

        context["recent_work_orders"] = (
            get_recent_work_orders(company)
        )

        context["operational_alerts"] = (
            get_operational_alerts(company)
        )

    context["recent_notifications"] = (
        get_recent_notifications(user)
    )

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )