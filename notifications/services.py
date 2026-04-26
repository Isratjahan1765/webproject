"""Notification service — creates notifications for system events."""

import logging
from django.contrib.auth.models import User

from .models import Notification, NotificationType

logger = logging.getLogger('sphwms')


class NotificationService:

    @staticmethod
    def _get_all_users():
        return User.objects.filter(is_active=True)

    @classmethod
    def notify_product_created(cls, product):
        for user in cls._get_all_users():
            Notification.objects.create(
                user=user,
                title=f'New Product Added: {product.name}',
                message=f'Product "{product.name}" (SKU: {product.sku}) has been added to the catalogue. Category: {product.get_category_display()}, Price: ৳{product.unit_price}',
                notification_type=NotificationType.PRODUCT_CREATED,
                link=f'/products/{product.pk}/',
            )

    @classmethod
    def notify_product_updated(cls, product, changes):
        changes_text = ', '.join(changes)
        for user in cls._get_all_users():
            Notification.objects.create(
                user=user,
                title=f'Product Updated: {product.name}',
                message=f'Product "{product.name}" has been updated. Changes: {changes_text}. All related records auto-updated via FK.',
                notification_type=NotificationType.PRODUCT_UPDATED,
                link=f'/products/{product.pk}/',
            )

    @classmethod
    def notify_arrival_confirmed(cls, arrival):
        for user in cls._get_all_users():
            Notification.objects.create(
                user=user,
                title=f'Arrival Confirmed: {arrival.batch_number}',
                message=f'Arrival batch {arrival.batch_number} has been confirmed. {arrival.total_items} item(s) added to inventory.',
                notification_type=NotificationType.ARRIVAL_CONFIRMED,
                link=f'/arrivals/{arrival.pk}/',
            )

    @classmethod
    def notify_pickup_confirmed(cls, pickup):
        for user in cls._get_all_users():
            Notification.objects.create(
                user=user,
                title=f'Pickup Confirmed: {pickup.pickup_number}',
                message=f'Pickup {pickup.pickup_number} confirmed for delivery to {pickup.destination}.',
                notification_type=NotificationType.PICKUP_CONFIRMED,
                link=f'/pickups/{pickup.pk}/',
            )

    @classmethod
    def notify_low_stock(cls, product, available_qty):
        for user in cls._get_all_users():
            Notification.objects.create(
                user=user,
                title=f'Low Stock Alert: {product.name}',
                message=f'Product "{product.name}" stock is low. Available: {available_qty}, Minimum: {product.minimum_stock}',
                notification_type=NotificationType.LOW_STOCK,
                link=f'/inventory/',
            )
