from celery import shared_task
from django.utils import timezone

from .models import Notification


@shared_task
def test_celery_task(name="Workforce Operations Platform"):
    return f"Celery task executed successfully for {name}."


@shared_task
def process_pending_notifications():
    notifications = Notification.objects.filter(
        status="UNREAD"
    ).order_by("created_at")[:50]

    processed_count = 0

    for notification in notifications:
        # For now, process in-app notifications.
        # Email/SMS/Push delivery can be connected later.
        if notification.channel == "IN_APP":
            notification.status = "READ"
            notification.read_at = timezone.now()

            notification.save(
                update_fields=[
                    "status",
                    "read_at",
                    "updated_at",
                ]
            )

            processed_count += 1

    return f"{processed_count} notification(s) processed successfully."