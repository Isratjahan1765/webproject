from rest_framework import serializers
from .models import Arrival, ArrivalItem


class ArrivalItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = ArrivalItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity',
                  'unit_price_at_arrival', 'quality_grade', 'line_total', 'notes']


class ArrivalListSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Arrival
        fields = ['id', 'batch_number', 'driver', 'driver_name', 'arrival_date',
                  'status', 'status_display', 'total_items', 'source_location', 'created_at']


class ArrivalDetailSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True, default=None)
    items = ArrivalItemSerializer(many=True, read_only=True)
    total_quantity = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Arrival
        fields = ['id', 'batch_number', 'driver', 'driver_name', 'arrival_date',
                  'status', 'status_display', 'source_location', 'notes',
                  'confirmed_by', 'confirmed_by_name', 'confirmed_at',
                  'items', 'total_quantity', 'total_value', 'created_at', 'updated_at']
        read_only_fields = ['batch_number', 'confirmed_by', 'confirmed_at', 'created_at', 'updated_at']
