from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import InventoryRecord, InventoryLog
from .serializers import InventoryRecordSerializer, InventoryLogSerializer


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset — inventory is modified via services, not direct API."""
    queryset = InventoryRecord.objects.select_related('product').filter(product__is_active=True)
    serializer_class = InventoryRecordSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['product__name', 'product__sku', 'warehouse_location']
    ordering = ['product__name']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        from django.db.models import Sum, Count, F
        data = InventoryRecord.objects.select_related('product').filter(
            product__is_active=True
        ).aggregate(
            total_products=Count('id'),
            total_quantity=Sum('total_quantity'),
            total_value=Sum(F('total_quantity') * F('product__unit_price')),
            total_reserved=Sum('reserved_quantity'),
        )
        for k, v in data.items():
            if v is None:
                data[k] = 0
            elif hasattr(v, 'quantize'):
                data[k] = float(v)
        return Response(data)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        record = self.get_object()
        logs = InventoryLog.objects.filter(product=record.product).order_by('-created_at')[:50]
        serializer = InventoryLogSerializer(logs, many=True)
        return Response(serializer.data)
