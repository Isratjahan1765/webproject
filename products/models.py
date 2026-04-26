"""
Product Catalogue — MASTER DATA SOURCE
=======================================
This is the Single Source of Truth for all product information.
All other modules reference products via ForeignKey (product_id).
No product data is duplicated in other tables.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class ProductCategory(models.TextChoices):
    """Post-harvest product categories."""
    GRAIN = 'grain', _('Grain / শস্য')
    RICE = 'rice', _('Rice / চাল')
    WHEAT = 'wheat', _('Wheat / গম')
    PULSE = 'pulse', _('Pulse / ডাল')
    OILSEED = 'oilseed', _('Oilseed / তৈলবীজ')
    SPICE = 'spice', _('Spice / মসলা')
    VEGETABLE = 'vegetable', _('Vegetable / সবজি')
    FRUIT = 'fruit', _('Fruit / ফল')
    FERTILIZER = 'fertilizer', _('Fertilizer / সার')
    SEED = 'seed', _('Seed / বীজ')
    OTHER = 'other', _('Other / অন্যান্য')


class ProductUnit(models.TextChoices):
    """Measurement units for products."""
    KG = 'kg', _('Kilogram / কেজি')
    TON = 'ton', _('Metric Ton / মেট্রিক টন')
    QUINTAL = 'quintal', _('Quintal / কুইন্টাল')
    MAUND = 'maund', _('Maund / মণ')
    LITER = 'liter', _('Liter / লিটার')
    PIECE = 'piece', _('Piece / পিস')
    BAG = 'bag', _('Bag / বস্তা')
    SACK = 'sack', _('Sack / বস্তা')


class Product(BaseModel):
    """
    MASTER ENTITY — Single Source of Truth.

    All modules fetch product data dynamically via FK.
    Cascade signals propagate updates to Inventory, Reports, Revenue, etc.
    """

    name = models.CharField(
        max_length=200,
        verbose_name=_('Product Name'),
        help_text=_('English name of the product'),
    )
    name_bn = models.CharField(
        max_length=200,
        verbose_name=_('পণ্যের নাম'),
        help_text=_('Bengali name of the product'),
        blank=True,
        default='',
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('SKU'),
        help_text=_('Stock Keeping Unit — unique product code'),
    )
    category = models.CharField(
        max_length=20,
        choices=ProductCategory.choices,
        default=ProductCategory.GRAIN,
        db_index=True,
        verbose_name=_('Category'),
    )
    unit = models.CharField(
        max_length=20,
        choices=ProductUnit.choices,
        default=ProductUnit.KG,
        verbose_name=_('Unit of Measurement'),
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Unit Price (৳)'),
        help_text=_('Current price per unit in BDT'),
    )
    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_('Minimum Stock Level'),
        help_text=_('Alert threshold for low stock'),
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Description'),
    )
    description_bn = models.TextField(
        blank=True,
        default='',
        verbose_name=_('বিবরণ'),
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Product Image'),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Active'),
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f'{self.name} ({self.sku})'

    @property
    def display_name(self):
        """Return bilingual display name."""
        if self.name_bn:
            return f'{self.name} / {self.name_bn}'
        return self.name

    @property
    def is_low_stock(self):
        """Check if current inventory is below minimum threshold."""
        try:
            inventory = self.inventory_record
            return inventory.available_quantity < self.minimum_stock
        except Exception:
            return False
