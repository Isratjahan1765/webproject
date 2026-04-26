"""
Report service layer — generates and caches monthly reports.
"""

import logging
from decimal import Decimal
from django.core.cache import cache
from django.db.models import Sum, Avg, F
from django.utils import timezone

from .models import MonthlyReport

logger = logging.getLogger('sphwms')


class ReportService:

    @staticmethod
    def generate_monthly_report(year, month):
        """Generate or refresh monthly report for all products."""
        from products.models import Product
        from arrivals.models import ArrivalItem, ArrivalStatus
        from pickups.models import PickupItem, PickupStatus

        products = Product.objects.filter(is_active=True)
        reports = []

        for product in products:
            # Total arrived
            arrived = ArrivalItem.objects.filter(
                product=product,
                arrival__status=ArrivalStatus.CONFIRMED,
                arrival__arrival_date__year=year,
                arrival__arrival_date__month=month,
            ).aggregate(
                total_qty=Sum('quantity'),
                total_val=Sum(F('quantity') * F('unit_price_at_arrival')),
            )

            # Total dispatched
            dispatched = PickupItem.objects.filter(
                product=product,
                pickup__status=PickupStatus.CONFIRMED,
                pickup__pickup_date__year=year,
                pickup__pickup_date__month=month,
            ).aggregate(
                total_qty=Sum('quantity'),
                total_val=Sum(F('quantity') * F('unit_price_at_pickup')),
            )

            report, created = MonthlyReport.objects.update_or_create(
                product=product, year=year, month=month,
                defaults={
                    'total_arrived': arrived['total_qty'] or 0,
                    'total_dispatched': dispatched['total_qty'] or 0,
                    'total_arrival_value': arrived['total_val'] or 0,
                    'total_dispatch_value': dispatched['total_val'] or 0,
                    'avg_unit_price': product.unit_price,
                }
            )
            reports.append(report)

        logger.info(f'Generated monthly reports for {year}/{month:02d}: {len(reports)} products')
        return reports

    @staticmethod
    def get_monthly_summary(year, month):
        """Get aggregated summary for a given month."""
        cache_key = f'monthly_report_{month}_{year}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        ReportService.generate_monthly_report(year, month)

        summary = MonthlyReport.objects.filter(
            year=year, month=month
        ).aggregate(
            total_arrived=Sum('total_arrived'),
            total_dispatched=Sum('total_dispatched'),
            total_arrival_value=Sum('total_arrival_value'),
            total_dispatch_value=Sum('total_dispatch_value'),
        )

        for k, v in summary.items():
            if v is None:
                summary[k] = Decimal('0')

        reports = MonthlyReport.objects.select_related('product').filter(
            year=year, month=month
        ).order_by('-total_dispatch_value')

        result = {'summary': summary, 'reports': reports}
        cache.set(cache_key, result, 600)
        return result

    @staticmethod
    def invalidate_product_reports(product):
        """Invalidate report caches when a product is updated."""
        now = timezone.now()
        cache.delete(f'monthly_report_{now.month}_{now.year}')
        logger.info(f'Report cache invalidated for product: {product.name}')
