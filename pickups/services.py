"""Pickup service layer."""

import logging
from django.db import transaction
from django.utils import timezone

from .models import Pickup, PickupItem, PickupStatus

logger = logging.getLogger('sphwms')


class PickupService:

    @staticmethod
    @transaction.atomic
    def confirm_pickup(pickup_id, user):
        """Confirm pickup — removes stock from inventory, records revenue."""
        pickup = Pickup.objects.select_for_update().get(pk=pickup_id)

        if pickup.status != PickupStatus.PENDING:
            raise ValueError(f'Cannot confirm pickup with status: {pickup.status}')

        # Remove stock for each item
        from inventory.services import InventoryService
        for item in pickup.items.select_related('product').all():
            InventoryService.remove_stock(
                product=item.product,
                quantity=item.quantity,
                source=f'Pickup {pickup.pickup_number}',
            )

        pickup.status = PickupStatus.CONFIRMED
        pickup.confirmed_by = user
        pickup.confirmed_at = timezone.now()
        pickup.save()

        # Record revenue
        from revenue.services import RevenueService
        RevenueService.record_pickup_revenue(pickup)

        logger.info(f'Pickup {pickup.pickup_number} confirmed by {user.username}')
        return pickup

    @staticmethod
    @transaction.atomic
    def cancel_pickup(pickup_id, user, reason=''):
        pickup = Pickup.objects.select_for_update().get(pk=pickup_id)
        if pickup.status not in [PickupStatus.PENDING, PickupStatus.CONFIRMED]:
            raise ValueError(f'Cannot cancel pickup with status: {pickup.status}')

        # If it was confirmed, release reserved stock
        if pickup.status == PickupStatus.CONFIRMED:
            from inventory.services import InventoryService
            for item in pickup.items.select_related('product').all():
                InventoryService.add_stock(
                    product=item.product,
                    quantity=item.quantity,
                    source=f'Pickup cancelled: {pickup.pickup_number}',
                )

        pickup.status = PickupStatus.CANCELLED
        pickup.notes = f'{pickup.notes}\nCancellation: {reason}'.strip()
        pickup.save()
        logger.info(f'Pickup {pickup.pickup_number} cancelled by {user.username}')
        return pickup

    @staticmethod
    def create_pickup_with_items(pickup_data, items_data):
        with transaction.atomic():
            pickup = Pickup.objects.create(**pickup_data)
            for item_data in items_data:
                item_data['pickup'] = pickup
                if 'unit_price_at_pickup' not in item_data:
                    item_data['unit_price_at_pickup'] = item_data['product'].unit_price
                PickupItem.objects.create(**item_data)
        return pickup
