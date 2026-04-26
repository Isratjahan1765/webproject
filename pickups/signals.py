"""Pickup signals."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pickup, PickupStatus

logger = logging.getLogger('sphwms')


@receiver(post_save, sender=Pickup)
def pickup_status_changed(sender, instance, **kwargs):
    if instance.status == PickupStatus.CONFIRMED:
        try:
            from core.services import DashboardService
            DashboardService.invalidate_cache()
        except Exception as e:
            logger.error(f'Failed to invalidate cache after pickup: {e}')
        try:
            from notifications.services import NotificationService
            NotificationService.notify_pickup_confirmed(instance)
        except Exception as e:
            logger.error(f'Failed to send pickup notification: {e}')
