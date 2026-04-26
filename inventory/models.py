"""
Inventory Management models.
Tracks stock levels per product — references Product via FK for live pricing.
No product data duplicated here.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel


class InventoryRecord(TimeStampedModel):
    """
    Single inventory record per product.
    Values are calculated dynamically from product.unit_price (FK reference).
    """

    product = models.OneToOneField(
        'products.Product', on_delete=models.CASCADE,
        related_name='inventory_record', verbose_name=_('Product'),
    )
    total_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        verbose_name=_('Total Quantity'),
    )
    reserved_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        verbose_name=_('Reserved Quantity'),
        help_text=_('Quantity reserved for pending pickups'),
    )
    warehouse_location = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_('Warehouse Location'),
        help_text=_('Physical location in warehouse (e.g., Section A, Rack 3)'),
    )
    last_restock_date = models.DateTimeField(null=True, blank=True)
    last_dispatch_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['product__name']
        verbose_name = _('Inventory Record')
        verbose_name_plural = _('Inventory Records')
        indexes = [
            models.Index(fields=['total_quantity']),
        ]

    def __str__(self):
        return f'{self.product.name} — {self.available_quantity} {self.product.unit}'

    @property
    def available_quantity(self):
        """Actual available stock = total - reserved."""
        return self.total_quantity - self.reserved_quantity

    @property
    def stock_value(self):
        """Live stock value calculated from current product price (FK reference)."""
        return self.total_quantity * self.product.unit_price

    @property
    def is_low_stock(self):
        return self.available_quantity < self.product.minimum_stock

    @property
    def stock_status(self):
        if self.available_quantity <= 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        return 'in_stock'


class InventoryLog(TimeStampedModel):
    """Audit log for all inventory changes."""

    class ChangeType(models.TextChoices):
        ADDITION = 'addition', _('Stock Addition')
        REMOVAL = 'removal', _('Stock Removal')
        RESERVATION = 'reservation', _('Stock Reserved')
        RELEASE = 'release', _('Reservation Released')
        ADJUSTMENT = 'adjustment', _('Manual Adjustment')

    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='inventory_logs', verbose_name=_('Product'),
    )
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)
    quantity_change = models.DecimalField(max_digits=14, decimal_places=2)
    quantity_before = models.DecimalField(max_digits=14, decimal_places=2)
    quantity_after = models.DecimalField(max_digits=14, decimal_places=2)
    source = models.CharField(
        max_length=200, blank=True, default='',
        help_text=_('Source reference (e.g., Arrival batch, Pickup number)'),
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Inventory Log')
        verbose_name_plural = _('Inventory Logs')

    def __str__(self):
        return f'{self.product.name}: {self.change_type} {self.quantity_change}'
