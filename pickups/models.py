"""
Pickup module — Confirm Delivery Pickup.
Tracks outgoing product shipments from the warehouse.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class PickupStatus(models.TextChoices):
    PENDING = 'pending', _('Pending / মুলতুবি')
    CONFIRMED = 'confirmed', _('Confirmed / নিশ্চিত')
    IN_TRANSIT = 'in_transit', _('In Transit / পথে')
    DELIVERED = 'delivered', _('Delivered / বিতরণ')
    CANCELLED = 'cancelled', _('Cancelled / বাতিল')


class Pickup(BaseModel):
    """Outgoing shipment from warehouse."""

    pickup_number = models.CharField(max_length=50, unique=True, verbose_name=_('Pickup Number'))
    driver = models.ForeignKey(
        'drivers.Driver', on_delete=models.PROTECT,
        related_name='pickups', verbose_name=_('Driver'),
    )
    pickup_date = models.DateTimeField(verbose_name=_('Pickup Date'), db_index=True)
    destination = models.CharField(max_length=300, verbose_name=_('Destination'))
    buyer_name = models.CharField(max_length=200, blank=True, default='', verbose_name=_('Buyer Name'))
    buyer_phone = models.CharField(max_length=20, blank=True, default='', verbose_name=_('Buyer Phone'))
    status = models.CharField(
        max_length=20, choices=PickupStatus.choices,
        default=PickupStatus.PENDING, db_index=True, verbose_name=_('Status'),
    )
    notes = models.TextField(blank=True, default='')
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='confirmed_pickups',
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-pickup_date']
        verbose_name = _('Pickup')
        verbose_name_plural = _('Pickups')
        indexes = [
            models.Index(fields=['status', 'pickup_date']),
        ]

    def __str__(self):
        return f'Pickup {self.pickup_number} → {self.destination}'

    def save(self, *args, **kwargs):
        if not self.pickup_number:
            self.pickup_number = f'PKP-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_quantity(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def total_value(self):
        total = 0
        for item in self.items.select_related('product').all():
            total += item.quantity * item.unit_price_at_pickup
        return total


class PickupItem(BaseModel):
    """Individual product line item within a pickup."""

    pickup = models.ForeignKey(
        Pickup, on_delete=models.CASCADE, related_name='items',
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT,
        related_name='pickup_items', verbose_name=_('Product'),
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Quantity'))
    unit_price_at_pickup = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_('Unit Price at Pickup'),
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def line_total(self):
        return self.quantity * self.unit_price_at_pickup
