"""
Revenue tracking models.
Records all financial transactions — references Product via FK.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel


class TransactionType(models.TextChoices):
    ARRIVAL = 'arrival', _('Goods Arrival (Expense)')
    DISPATCH = 'dispatch', _('Goods Dispatch (Revenue)')
    ADJUSTMENT = 'adjustment', _('Manual Adjustment')
    REFUND = 'refund', _('Refund')


class RevenueEntry(TimeStampedModel):
    """Individual revenue/expense transaction line."""

    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='revenue_entries', verbose_name=_('Product'),
    )
    transaction_type = models.CharField(
        max_length=20, choices=TransactionType.choices,
        db_index=True, verbose_name=_('Transaction Type'),
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('Quantity'))
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_('Unit Price'),
        help_text=_('Price at time of transaction'),
    )
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('Total Amount'))
    transaction_date = models.DateTimeField(db_index=True, verbose_name=_('Transaction Date'))
    reference = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_('Reference'),
        help_text=_('e.g., Arrival batch or Pickup number'),
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = _('Revenue Entry')
        verbose_name_plural = _('Revenue Entries')
        indexes = [
            models.Index(fields=['transaction_type', 'transaction_date']),
            models.Index(fields=['product', 'transaction_date']),
        ]

    def __str__(self):
        return f'{self.get_transaction_type_display()} — {self.product.name} ৳{self.total_amount}'

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
