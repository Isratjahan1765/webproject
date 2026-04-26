"""
Arrival service layer — business logic for confirming arrivals
and updating inventory.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import Arrival, ArrivalItem, ArrivalStatus

logger = logging.getLogger('sphwms')


class ArrivalService:

    @staticmethod
    @transaction.atomic
    def confirm_arrival(arrival_id, user):
        """
        Confirm an arrival and update inventory for all items.
        This is the core operation that links arrivals → inventory.
        """
        arrival = Arrival.objects.select_for_update().get(pk=arrival_id)

        if arrival.status != ArrivalStatus.PENDING:
            raise ValueError(f'Cannot confirm arrival with status: {arrival.status}')

        arrival.status = ArrivalStatus.CONFIRMED
        arrival.confirmed_by = user
        arrival.confirmed_at = timezone.now()
        arrival.save()

        # Update inventory for each item
        from inventory.services import InventoryService

        for item in arrival.items.select_related('product').all():
            InventoryService.add_stock(
                product=item.product,
                quantity=item.quantity,
                source=f'Arrival {arrival.batch_number}',
            )

        # Create revenue entry for arrival (incoming goods value)
        from revenue.services import RevenueService
        RevenueService.record_arrival_revenue(arrival)

        logger.info(f'Arrival {arrival.batch_number} confirmed by {user.username}')
        return arrival

    @staticmethod
    @transaction.atomic
    def reject_arrival(arrival_id, user, reason=''):
        arrival = Arrival.objects.select_for_update().get(pk=arrival_id)
        if arrival.status != ArrivalStatus.PENDING:
            raise ValueError(f'Cannot reject arrival with status: {arrival.status}')

        arrival.status = ArrivalStatus.REJECTED
        arrival.confirmed_by = user
        arrival.confirmed_at = timezone.now()
        arrival.notes = f'{arrival.notes}\nRejection reason: {reason}'.strip()
        arrival.save()
        logger.info(f'Arrival {arrival.batch_number} rejected by {user.username}')
        return arrival

    @staticmethod
    def create_arrival_with_items(arrival_data, items_data):
        """Create arrival with line items in a single transaction."""
        with transaction.atomic():
            arrival = Arrival.objects.create(**arrival_data)
            for item_data in items_data:
                item_data['arrival'] = arrival
                # Snapshot the current product price
                if 'unit_price_at_arrival' not in item_data:
                    item_data['unit_price_at_arrival'] = item_data['product'].unit_price
                ArrivalItem.objects.create(**item_data)
        return arrival
