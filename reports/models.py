"""
Monthly Reports models.
Aggregated data per product per month — references Product via FK.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel


class MonthlyReport(TimeStampedModel):
    """Aggregated monthly report per product."""

    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='monthly_reports', verbose_name=_('Product'),
    )
    year = models.PositiveIntegerField(verbose_name=_('Year'), db_index=True)
    month = models.PositiveIntegerField(verbose_name=_('Month'), db_index=True)
    total_arrived = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('Total Arrived'))
    total_dispatched = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('Total Dispatched'))
    total_arrival_value = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('Arrival Value'))
    total_dispatch_value = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('Dispatch Value'))
    opening_stock = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('Opening Stock'))
    closing_stock = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('Closing Stock'))
    avg_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Avg Unit Price'))

    class Meta:
        ordering = ['-year', '-month']
        verbose_name = _('Monthly Report')
        verbose_name_plural = _('Monthly Reports')
        unique_together = ['product', 'year', 'month']
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['product', 'year', 'month']),
        ]

    def __str__(self):
        return f'{self.product.name} — {self.year}/{self.month:02d}'

    @property
    def net_change(self):
        return self.total_arrived - self.total_dispatched

    @property
    def revenue(self):
        """Revenue = dispatch value (what was sold/shipped out)."""
        return self.total_dispatch_value
