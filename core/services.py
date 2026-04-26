"""
Dashboard service layer.
Aggregates data from all modules for the main dashboard analytics.
Uses select_related/prefetch_related to avoid N+1 queries.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone

logger = logging.getLogger('sphwms')


class DashboardService:
    """Aggregation service for dashboard analytics."""

    CACHE_TIMEOUT = 300  # 5 minutes

    @classmethod
    def get_overview_stats(cls):
        """Get high-level KPI stats for the dashboard."""
        cache_key = 'dashboard_overview_stats'
        stats = cache.get(cache_key)

        if stats is not None:
            return stats

        from products.models import Product
        from inventory.models import InventoryRecord
        from arrivals.models import Arrival
        from pickups.models import Pickup
        from revenue.models import RevenueEntry
        from drivers.models import Driver

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total active products
        total_products = Product.objects.filter(is_active=True).count()

        # Total inventory value (quantity × current product price)
        inventory_data = InventoryRecord.objects.select_related('product').filter(
            product__is_active=True
        ).aggregate(
            sum_quantity=Sum('total_quantity'),
            sum_value=Sum(F('total_quantity') * F('product__unit_price')),
        )

        # Monthly arrivals & pickups
        monthly_arrivals = Arrival.objects.filter(
            arrival_date__gte=month_start
        ).count()

        monthly_pickups = Pickup.objects.filter(
            pickup_date__gte=month_start
        ).count()

        # Monthly revenue
        monthly_revenue = RevenueEntry.objects.filter(
            transaction_date__gte=month_start
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')

        # Available drivers
        available_drivers = Driver.objects.filter(is_available=True).count()

        # Pending arrivals (not yet confirmed)
        pending_arrivals = Arrival.objects.filter(status='pending').count()

        # Pending pickups
        pending_pickups = Pickup.objects.filter(status='pending').count()

        stats = {
            'total_products': total_products,
            'total_inventory_quantity': inventory_data['sum_quantity'] or 0,
            'total_inventory_value': inventory_data['sum_value'] or Decimal('0.00'),
            'monthly_arrivals': monthly_arrivals,
            'monthly_pickups': monthly_pickups,
            'monthly_revenue': monthly_revenue,
            'available_drivers': available_drivers,
            'pending_arrivals': pending_arrivals,
            'pending_pickups': pending_pickups,
        }

        cache.set(cache_key, stats, cls.CACHE_TIMEOUT)
        return stats

    @classmethod
    def get_revenue_chart_data(cls, months=6):
        """Get monthly revenue data for chart rendering."""
        from revenue.models import RevenueEntry

        now = timezone.now()
        data = []

        for i in range(months - 1, -1, -1):
            date = now - timedelta(days=30 * i)
            month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if date.month == 12:
                month_end = month_start.replace(year=date.year + 1, month=1)
            else:
                month_end = month_start.replace(month=date.month + 1)

            revenue = RevenueEntry.objects.filter(
                transaction_date__gte=month_start,
                transaction_date__lt=month_end,
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

            data.append({
                'month': month_start.strftime('%b %Y'),
                'revenue': float(revenue),
            })

        return data

    @classmethod
    def get_top_products(cls, limit=5):
        """Get top products by inventory quantity."""
        from inventory.models import InventoryRecord

        return InventoryRecord.objects.select_related('product').filter(
            product__is_active=True
        ).order_by('-total_quantity')[:limit]

    @classmethod
    def get_recent_arrivals(cls, limit=5):
        """Get most recent arrivals with related data."""
        from arrivals.models import Arrival

        return Arrival.objects.select_related(
            'driver', 'confirmed_by'
        ).prefetch_related(
            'items__product'
        ).order_by('-arrival_date')[:limit]

    @classmethod
    def get_recent_pickups(cls, limit=5):
        """Get most recent pickups with related data."""
        from pickups.models import Pickup

        return Pickup.objects.select_related(
            'driver', 'confirmed_by'
        ).prefetch_related(
            'items__product'
        ).order_by('-pickup_date')[:limit]

    @classmethod
    def get_inventory_distribution(cls):
        """Get inventory distribution by product category for pie chart."""
        from inventory.models import InventoryRecord

        return InventoryRecord.objects.select_related('product').filter(
            product__is_active=True
        ).values(
            'product__category'
        ).annotate(
            total=Sum('total_quantity'),
            count=Count('id'),
        ).order_by('-total')

    @classmethod
    def invalidate_cache(cls):
        """Clear all dashboard caches — called by signals."""
        cache.delete('dashboard_overview_stats')
        logger.info('Dashboard cache invalidated')
