"""Arrival signals — post-confirm updates."""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Arrival, ArrivalStatus

logger = logging.getLogger('sphwms')


@receiver(post_save, sender=Arrival)
def arrival_status_changed(sender, instance, **kwargs):
    """When arrival is confirmed, invalidate dashboard cache."""
    if instance.status == ArrivalStatus.CONFIRMED:
        try:
            from core.services import DashboardService
            DashboardService.invalidate_cache()
        except Exception as e:
            logger.error(f'Failed to invalidate cache after arrival confirm: {e}')

        try:
            from notifications.services import NotificationService
            NotificationService.notify_arrival_confirmed(instance)
        except Exception as e:
            logger.error(f'Failed to send arrival notification: {e}')
