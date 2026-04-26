"""Revenue service layer."""

import logging
from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.cache import cache

from .models import RevenueEntry, TransactionType

logger = logging.getLogger('sphwms')


class RevenueService:

    @staticmethod
    def record_arrival_revenue(arrival):
        """Record expense entries for a confirmed arrival."""
        for item in arrival.items.select_related('product').all():
            RevenueEntry.objects.create(
                product=item.product,
                transaction_type=TransactionType.ARRIVAL,
                quantity=item.quantity,
                unit_price=item.unit_price_at_arrival,
                total_amount=item.quantity * item.unit_price_at_arrival,
                transaction_date=arrival.arrival_date,
                reference=f'ARR:{arrival.batch_number}',
            )
        logger.info(f'Revenue entries created for arrival {arrival.batch_number}')

    @staticmethod
    def record_pickup_revenue(pickup):
        """Record revenue entries for a confirmed pickup/dispatch."""
        for item in pickup.items.select_related('product').all():
            RevenueEntry.objects.create(
                product=item.product,
                transaction_type=TransactionType.DISPATCH,
                quantity=item.quantity,
                unit_price=item.unit_price_at_pickup,
                total_amount=item.quantity * item.unit_price_at_pickup,
                transaction_date=pickup.pickup_date,
                reference=f'PKP:{pickup.pickup_number}',
            )
        logger.info(f'Revenue entries created for pickup {pickup.pickup_number}')

    @staticmethod
    def get_revenue_summary(year=None, month=None):
        """Get revenue vs expense summary."""
        qs = RevenueEntry.objects.all()
        if year:
            qs = qs.filter(transaction_date__year=year)
        if month:
            qs = qs.filter(transaction_date__month=month)

        income = qs.filter(
            transaction_type=TransactionType.DISPATCH
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        expense = qs.filter(
            transaction_type=TransactionType.ARRIVAL
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        return {
            'total_income': income,
            'total_expense': expense,
            'net_profit': income - expense,
            'transaction_count': qs.count(),
        }

    @staticmethod
    def get_product_revenue(product_id, year=None):
        """Get revenue breakdown for a specific product."""
        qs = RevenueEntry.objects.filter(product_id=product_id)
        if year:
            qs = qs.filter(transaction_date__year=year)
        return qs.values('transaction_type').annotate(
            total=Sum('total_amount'),
            qty=Sum('quantity'),
        )
