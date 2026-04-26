"""Notification models."""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel


class NotificationType(models.TextChoices):
    PRODUCT_CREATED = 'product_created', _('Product Created')
    PRODUCT_UPDATED = 'product_updated', _('Product Updated')
    ARRIVAL_CONFIRMED = 'arrival_confirmed', _('Arrival Confirmed')
    PICKUP_CONFIRMED = 'pickup_confirmed', _('Pickup Confirmed')
    LOW_STOCK = 'low_stock', _('Low Stock Alert')
    SYSTEM = 'system', _('System Notification')


class Notification(TimeStampedModel):
    """User notifications for system events."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    message = models.TextField(verbose_name=_('Message'))
    notification_type = models.CharField(
        max_length=30, choices=NotificationType.choices,
        default=NotificationType.SYSTEM, db_index=True,
    )
    is_read = models.BooleanField(default=False, db_index=True)
    link = models.CharField(max_length=300, blank=True, default='', help_text=_('URL to navigate to'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'{self.title} → {self.user.username}'

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
