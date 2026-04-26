from rest_framework import serializers
from .models import Pickup, PickupItem


class PickupItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = PickupItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price_at_pickup', 'line_total', 'notes']


class PickupSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = PickupItemSerializer(many=True, read_only=True)
    total_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Pickup
        fields = ['id', 'pickup_number', 'driver', 'driver_name', 'pickup_date',
                  'destination', 'buyer_name', 'buyer_phone', 'status', 'status_display',
                  'notes', 'confirmed_by', 'confirmed_at', 'items', 'total_value',
                  'created_at', 'updated_at']
        read_only_fields = ['pickup_number', 'confirmed_by', 'confirmed_at']
