from rest_framework import serializers
from .models import RevenueEntry


class RevenueEntrySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = RevenueEntry
        fields = ['id', 'product', 'product_name', 'transaction_type',
                  'transaction_type_display', 'quantity', 'unit_price',
                  'total_amount', 'transaction_date', 'reference', 'notes', 'created_at']
