"""
Inventory service layer.
Handles stock add/remove/reserve operations with audit logging.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from .models import InventoryRecord, InventoryLog

logger = logging.getLogger('sphwms')


class InventoryService:

    @staticmethod
    def initialize_inventory(product):
        """Create initial inventory record for a new product (called by product signal)."""
        record, created = InventoryRecord.objects.get_or_create(
            product=product,
            defaults={'total_quantity': 0, 'reserved_quantity': 0},
        )
        if created:
            logger.info(f'Initialized inventory for: {product.name}')
        return record

    @staticmethod
    @transaction.atomic
    def add_stock(product, quantity, source=''):
        """Add stock to inventory (e.g., from confirmed arrival)."""
        record, _ = InventoryRecord.objects.get_or_create(product=product)
        old_qty = record.total_quantity
        record.total_quantity += Decimal(str(quantity))
        record.last_restock_date = timezone.now()
        record.save()

        InventoryLog.objects.create(
            product=product,
            change_type=InventoryLog.ChangeType.ADDITION,
            quantity_change=Decimal(str(quantity)),
            quantity_before=old_qty,
            quantity_after=record.total_quantity,
            source=source,
        )
        logger.info(f'Stock added: {product.name} +{quantity} (source: {source})')
        InventoryService._invalidate_cache()
        return record

    @staticmethod
    @transaction.atomic
    def remove_stock(product, quantity, source=''):
        """Remove stock from inventory (e.g., from confirmed pickup)."""
        record = InventoryRecord.objects.select_for_update().get(product=product)

        if record.available_quantity < Decimal(str(quantity)):
            raise ValueError(
                f'Insufficient stock for {product.name}. '
                f'Available: {record.available_quantity}, Requested: {quantity}'
            )

        old_qty = record.total_quantity
        record.total_quantity -= Decimal(str(quantity))
        record.last_dispatch_date = timezone.now()
        record.save()

        InventoryLog.objects.create(
            product=product,
            change_type=InventoryLog.ChangeType.REMOVAL,
            quantity_change=-Decimal(str(quantity)),
            quantity_before=old_qty,
            quantity_after=record.total_quantity,
            source=source,
        )
        logger.info(f'Stock removed: {product.name} -{quantity} (source: {source})')
        InventoryService._invalidate_cache()
        return record

    @staticmethod
    @transaction.atomic
    def reserve_stock(product, quantity, source=''):
        """Reserve stock for a pending pickup."""
        record = InventoryRecord.objects.select_for_update().get(product=product)
        if record.available_quantity < Decimal(str(quantity)):
            raise ValueError(f'Insufficient available stock for reservation')

        record.reserved_quantity += Decimal(str(quantity))
        record.save()

        InventoryLog.objects.create(
            product=product,
            change_type=InventoryLog.ChangeType.RESERVATION,
            quantity_change=Decimal(str(quantity)),
            quantity_before=record.total_quantity,
            quantity_after=record.total_quantity,
            source=source,
            notes=f'Reserved: {quantity}',
        )
        return record

    @staticmethod
    @transaction.atomic
    def release_reservation(product, quantity, source=''):
        """Release a stock reservation (e.g., pickup cancelled)."""
        record = InventoryRecord.objects.select_for_update().get(product=product)
        record.reserved_quantity = max(Decimal('0'), record.reserved_quantity - Decimal(str(quantity)))
        record.save()

        InventoryLog.objects.create(
            product=product,
            change_type=InventoryLog.ChangeType.RELEASE,
            quantity_change=-Decimal(str(quantity)),
            quantity_before=record.total_quantity,
            quantity_after=record.total_quantity,
            source=source,
        )
        return record

    @staticmethod
    def recalculate_inventory_value(product):
        """
        Called by product signal when price changes.
        Since stock_value is a property computed from product.unit_price (FK),
        we only need to invalidate caches — no data to update.
        """
        logger.info(f'Price changed for {product.name} — inventory values auto-updated via FK')
        InventoryService._invalidate_cache()

    @staticmethod
    def get_summary():
        """Get inventory summary stats."""
        from django.db.models import Sum, F
        return InventoryRecord.objects.select_related('product').filter(
            product__is_active=True
        ).aggregate(
            total_products=models.Count('id'),
            total_quantity=Sum('total_quantity'),
            total_value=Sum(F('total_quantity') * F('product__unit_price')),
            total_reserved=Sum('reserved_quantity'),
        )

    @staticmethod
    def _invalidate_cache():
        cache.delete('dashboard_overview_stats')
        cache.delete('inventory_summary')
