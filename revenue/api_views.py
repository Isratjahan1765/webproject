from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import RevenueEntry
from .serializers import RevenueEntrySerializer
from .services import RevenueService


class RevenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RevenueEntry.objects.select_related('product')
    serializer_class = RevenueEntrySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['transaction_type', 'product']
    ordering = ['-transaction_date']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        now = timezone.now()
        year = int(request.query_params.get('year', now.year))
        month = request.query_params.get('month')
        month = int(month) if month else None
        data = RevenueService.get_revenue_summary(year=year, month=month)
        return Response({k: float(v) if hasattr(v, 'quantize') else v for k, v in data.items()})
