"""
Product service layer.
Business logic for product CRUD operations, isolated from views.
"""

import logging
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Product

logger = logging.getLogger('sphwms')


class ProductService:
    """Business logic for Product management."""

    @staticmethod
    def get_all_products(include_inactive=False):
        """Get all products with optional inactive filter."""
        qs = Product.objects.all()
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs

    @staticmethod
    def get_product_by_id(product_id):
        """Get a single product by ID."""
        return Product.objects.get(pk=product_id)

    @staticmethod
    def get_products_by_category(category):
        """Get active products filtered by category."""
        return Product.objects.filter(
            category=category,
            is_active=True,
        )

    @staticmethod
    def search_products(query):
        """Search products by name, SKU, or category."""
        from django.db.models import Q
        return Product.objects.filter(
            Q(name__icontains=query) |
            Q(name_bn__icontains=query) |
            Q(sku__icontains=query) |
            Q(category__icontains=query),
            is_active=True,
        )

    @staticmethod
    @transaction.atomic
    def create_product(data):
        """
        Create a new product. The post_save signal will
        automatically initialize inventory and send notifications.
        """
        product = Product(**data)
        product.full_clean()
        product.save()
        logger.info(f'ProductService: Created product {product.name}')
        return product

    @staticmethod
    @transaction.atomic
    def update_product(product_id, data):
        """
        Update a product. The post_save signal will automatically
        cascade changes to all dependent modules.
        """
        product = Product.objects.select_for_update().get(pk=product_id)
        for field, value in data.items():
            setattr(product, field, value)
        product.full_clean()
        product.save()
        logger.info(f'ProductService: Updated product {product.name}')
        return product

    @staticmethod
    @transaction.atomic
    def deactivate_product(product_id):
        """Soft-deactivate a product (set is_active=False)."""
        product = Product.objects.get(pk=product_id)
        product.is_active = False
        product.save(update_fields=['is_active', 'updated_at'])
        logger.info(f'ProductService: Deactivated product {product.name}')
        return product

    @staticmethod
    @transaction.atomic
    def delete_product(product_id):
        """Soft-delete a product."""
        product = Product.objects.get(pk=product_id)
        product.soft_delete()
        logger.info(f'ProductService: Soft-deleted product {product.name}')
        return product

    @staticmethod
    def get_low_stock_products():
        """Get products below minimum stock threshold."""
        from inventory.models import InventoryRecord
        from django.db.models import F

        return InventoryRecord.objects.select_related('product').filter(
            product__is_active=True,
            available_quantity__lt=F('product__minimum_stock'),
        )

    @staticmethod
    def generate_sku(category, sequence=None):
        """Auto-generate SKU based on category and sequence."""
        prefix = category[:3].upper()
        if sequence is None:
            last_product = Product.all_objects.filter(
                sku__startswith=prefix
            ).order_by('-sku').first()
            if last_product:
                try:
                    last_num = int(last_product.sku.split('-')[-1])
                    sequence = last_num + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
        return f'{prefix}-{sequence:05d}'
