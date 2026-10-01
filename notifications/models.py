from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    INFO = "INFO", "Information"
    SUCCESS = "SUCCESS", "Success"
    WARNING = "WARNING", "Warning"
    ERROR = "ERROR", "Error"
    REMINDER = "REMINDER", "Reminder"


class NotificationChannel(models.TextChoices):
    IN_APP = "IN_APP", "In App"
    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"
    PUSH = "PUSH", "Push"


class NotificationPriority(models.TextChoices):
    LOW = "LOW", "Low"
    NORMAL = "NORMAL", "Normal"
    HIGH = "HIGH", "High"
    URGENT = "URGENT", "Urgent"


class NotificationStatus(models.TextChoices):
    UNREAD = "UNREAD", "Unread"
    READ = "READ", "Read"
    ARCHIVED = "ARCHIVED", "Archived"


class Notification(models.Model):

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
    )

    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    title = models.CharField(
        max_length=250,
    )

    message = models.TextField()

    object_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Optional type of related object, "
            "for example WorkOrder or Invoice."
        ),
    )

    object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.UNREAD,
    )

    read_at = models.DateTimeField(
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
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return (
            f"{self.recipient.email} - "
            f"{self.title}"
        )