from rest_framework import serializers
from .models import Driver


class DriverSerializer(serializers.ModelSerializer):
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    total_trips = serializers.IntegerField(read_only=True)

    class Meta:
        model = Driver
        fields = [
            'id', 'name', 'name_bn', 'phone', 'alt_phone', 'nid_number',
            'license_number', 'vehicle_type', 'vehicle_type_display',
            'vehicle_number', 'address', 'photo', 'is_available',
            'total_trips', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
