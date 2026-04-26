"""
Product signals — Event-driven cascade mechanism.
==================================================
When a Product is created/updated/deleted, these signals propagate changes
to all dependent modules (Inventory, Reports, Revenue, Notifications).
This ensures the Single Source of Truth architecture is maintained.
"""

import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import Product

logger = logging.getLogger('sphwms')


@receiver(pre_save, sender=Product)
def capture_old_product_state(sender, instance, **kwargs):
    """Capture the product state before save for change detection."""
    if instance.pk:
        try:
            old_instance = Product.all_objects.get(pk=instance.pk)
            instance._old_unit_price = old_instance.unit_price
            instance._old_name = old_instance.name
            instance._old_category = old_instance.category
            instance._price_changed = old_instance.unit_price != instance.unit_price
            instance._name_changed = old_instance.name != instance.name
        except Product.DoesNotExist:
            instance._price_changed = False
            instance._name_changed = False
    else:
        instance._price_changed = False
        instance._name_changed = False


@receiver(post_save, sender=Product)
def product_post_save_handler(sender, instance, created, **kwargs):
    """
    Central cascade handler for product changes.
    Dispatches to relevant services based on what changed.
    """
    if created:
        _handle_product_created(instance)
    else:
        _handle_product_updated(instance)


@receiver(post_delete, sender=Product)
def product_post_delete_handler(sender, instance, **kwargs):
    """Handle product hard deletion — clean up related records."""
    logger.warning(f'Product hard deleted: {instance.name} (ID: {instance.pk})')
    _invalidate_all_caches()


def _handle_product_created(product):
    """When a new product is created, initialize its inventory record."""
    logger.info(f'New product created: {product.name} (SKU: {product.sku})')

    # Create initial inventory record
    try:
        from inventory.services import InventoryService
        InventoryService.initialize_inventory(product)
    except Exception as e:
        logger.error(f'Failed to initialize inventory for {product.name}: {e}')

    # Create notification
    try:
        from notifications.services import NotificationService
        NotificationService.notify_product_created(product)
    except Exception as e:
        logger.error(f'Failed to create notification for new product: {e}')

    _invalidate_all_caches()


def _handle_product_updated(product):
    """When a product is updated, cascade changes to dependent modules."""
    changes = []

    if getattr(product, '_price_changed', False):
        old_price = getattr(product, '_old_unit_price', None)
        changes.append(f'price: {old_price} → {product.unit_price}')

        # Recalculate inventory values (they reference product.unit_price via FK)
        try:
            from inventory.services import InventoryService
            InventoryService.recalculate_inventory_value(product)
        except Exception as e:
            logger.error(f'Failed to recalculate inventory for {product.name}: {e}')

    if getattr(product, '_name_changed', False):
        old_name = getattr(product, '_old_name', None)
        changes.append(f'name: {old_name} → {product.name}')

    if changes:
        logger.info(f'Product updated: {product.name} — Changes: {", ".join(changes)}')

        # Invalidate report caches
        try:
            from reports.services import ReportService
            ReportService.invalidate_product_reports(product)
        except Exception as e:
            logger.error(f'Failed to invalidate reports: {e}')

        # Create update notification
        try:
            from notifications.services import NotificationService
            NotificationService.notify_product_updated(product, changes)
        except Exception as e:
            logger.error(f'Failed to create update notification: {e}')

    _invalidate_all_caches()


def _invalidate_all_caches():
    """Invalidate all caches affected by product changes."""
    try:
        from core.services import DashboardService
        DashboardService.invalidate_cache()
    except Exception as e:
        logger.error(f'Failed to invalidate dashboard cache: {e}')
