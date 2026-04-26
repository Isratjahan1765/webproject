from rest_framework import serializers
from .models import MonthlyReport


class MonthlyReportSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    net_change = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    revenue = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = MonthlyReport
        fields = ['id', 'product', 'product_name', 'product_sku', 'year', 'month',
                  'total_arrived', 'total_dispatched', 'total_arrival_value',
                  'total_dispatch_value', 'opening_stock', 'closing_stock',
                  'avg_unit_price', 'net_change', 'revenue', 'created_at']
