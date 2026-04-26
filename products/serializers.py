"""
Product serializers for REST API.
"""

from rest_framework import serializers
from .models import Product, ProductCategory, ProductUnit


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'name_bn', 'sku', 'category', 'category_display',
            'unit', 'unit_display', 'unit_price', 'is_active', 'is_low_stock',
            'created_at', 'updated_at',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail/create/update views."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'name_bn', 'sku', 'category', 'category_display',
            'unit', 'unit_display', 'unit_price', 'minimum_stock',
            'description', 'description_bn', 'image', 'is_active',
            'is_low_stock', 'display_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Unit price must be greater than zero.')
        return value

    def validate_sku(self, value):
        """Ensure SKU uniqueness on create."""
        if self.instance is None:  # Create
            if Product.objects.filter(sku=value).exists():
                raise serializers.ValidationError('A product with this SKU already exists.')
        return value
