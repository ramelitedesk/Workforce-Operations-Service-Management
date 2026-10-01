from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Notification


@transaction.atomic
def create_notification(
    *,
    recipient,
    title,
    message,
    notification_type="INFO",
    channel="IN_APP",
    priority="NORMAL",
    object_type="",
    object_id=None,
):
    """
    Create an in-app/system notification for a user.
    """

    if not recipient:
        raise ValidationError(
            "Notification recipient is required."
        )

    if not title or not title.strip():
        raise ValidationError(
            "Notification title is required."
        )

    if not message or not message.strip():
        raise ValidationError(
            "Notification message is required."
        )

    if object_id is not None and not object_type:
        raise ValidationError(
            "object_type is required when object_id is provided."
        )

    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        channel=channel,
        priority=priority,
        title=title.strip(),
        message=message.strip(),
        object_type=object_type,
        object_id=object_id,
        status="UNREAD",
    )

    return notification


@transaction.atomic
def mark_notification_as_read(notification):
    """
    Mark a notification as read.
    """

    if notification.status == "ARCHIVED":
        raise ValidationError(
            "Archived notifications cannot be marked as read."
        )

    notification.status = "READ"
    notification.read_at = timezone.now()

    notification.save(
        update_fields=[
            "status",
            "read_at",
            "updated_at",
        ]
    )

    return notification


@transaction.atomic
def archive_notification(notification):
    """
    Archive a notification.
    """

    notification.status = "ARCHIVED"

    if not notification.read_at:
        notification.read_at = timezone.now()

    notification.save(
        update_fields=[
            "status",
            "read_at",
            "updated_at",
        ]
    )

    return notification