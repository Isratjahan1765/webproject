"""
Arrivals module — Confirm New Arrivals.
Tracks incoming product shipments to the warehouse.
Product data is referenced via FK — never duplicated.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class ArrivalStatus(models.TextChoices):
    PENDING = 'pending', _('Pending / মুলতুবি')
    CONFIRMED = 'confirmed', _('Confirmed / নিশ্চিত')
    REJECTED = 'rejected', _('Rejected / প্রত্যাখ্যাত')
    CANCELLED = 'cancelled', _('Cancelled / বাতিল')


class QualityGrade(models.TextChoices):
    A = 'A', _('Grade A — Premium')
    B = 'B', _('Grade B — Standard')
    C = 'C', _('Grade C — Below Standard')
    D = 'D', _('Grade D — Damaged')


class Arrival(BaseModel):
    """Incoming shipment batch to the warehouse."""

    batch_number = models.CharField(
        max_length=50, unique=True, verbose_name=_('Batch Number'),
        help_text=_('Auto-generated unique batch identifier'),
    )
    driver = models.ForeignKey(
        'drivers.Driver', on_delete=models.PROTECT,
        related_name='arrivals', verbose_name=_('Driver'),
    )
    arrival_date = models.DateTimeField(verbose_name=_('Arrival Date'), db_index=True)
    status = models.CharField(
        max_length=20, choices=ArrivalStatus.choices,
        default=ArrivalStatus.PENDING, db_index=True, verbose_name=_('Status'),
    )
    source_location = models.CharField(max_length=200, blank=True, default='', verbose_name=_('Source Location'))
    notes = models.TextField(blank=True, default='', verbose_name=_('Notes'))
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='confirmed_arrivals', verbose_name=_('Confirmed By'),
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-arrival_date']
        verbose_name = _('Arrival')
        verbose_name_plural = _('Arrivals')
        indexes = [
            models.Index(fields=['status', 'arrival_date']),
            models.Index(fields=['batch_number']),
        ]

    def __str__(self):
        return f'Arrival {self.batch_number} — {self.get_status_display()}'

    def save(self, *args, **kwargs):
        if not self.batch_number:
            self.batch_number = f'ARR-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_quantity(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def total_value(self):
        """Calculate total value using current product prices (FK reference)."""
        total = 0
        for item in self.items.select_related('product').all():
            total += item.quantity * item.unit_price_at_arrival
        return total


class ArrivalItem(BaseModel):
    """Individual product line item within an arrival batch."""

    arrival = models.ForeignKey(
        Arrival, on_delete=models.CASCADE, related_name='items', verbose_name=_('Arrival'),
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT,
        related_name='arrival_items', verbose_name=_('Product'),
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Quantity'))
    unit_price_at_arrival = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_('Unit Price at Arrival'),
        help_text=_('Snapshot of price at arrival time — product.unit_price is the live reference'),
    )
    quality_grade = models.CharField(
        max_length=5, choices=QualityGrade.choices,
        default=QualityGrade.A, verbose_name=_('Quality Grade'),
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['id']
        verbose_name = _('Arrival Item')
        verbose_name_plural = _('Arrival Items')

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def line_total(self):
        return self.quantity * self.unit_price_at_arrival
