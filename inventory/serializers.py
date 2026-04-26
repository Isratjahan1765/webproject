from rest_framework import serializers
from .models import InventoryRecord, InventoryLog


class InventoryRecordSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_unit = serializers.CharField(source='product.get_unit_display', read_only=True)
    product_unit_price = serializers.DecimalField(source='product.unit_price', max_digits=12, decimal_places=2, read_only=True)
    available_quantity = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    stock_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = InventoryRecord
        fields = ['id', 'product', 'product_name', 'product_sku', 'product_unit',
                  'product_unit_price', 'total_quantity', 'reserved_quantity',
                  'available_quantity', 'stock_value', 'stock_status',
                  'warehouse_location', 'last_restock_date', 'last_dispatch_date',
                  'created_at', 'updated_at']


class InventoryLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)

    class Meta:
        model = InventoryLog
        fields = ['id', 'product', 'product_name', 'change_type', 'change_type_display',
                  'quantity_change', 'quantity_before', 'quantity_after', 'source', 'notes', 'created_at']
