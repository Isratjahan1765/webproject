from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MonthlyReport
from .serializers import MonthlyReportSerializer
from .services import ReportService
from django.utils import timezone


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonthlyReport.objects.select_related('product')
    serializer_class = MonthlyReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['year', 'month', 'product']
    ordering = ['-year', '-month']

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        now = timezone.now()
        year = int(request.query_params.get('year', now.year))
        month = int(request.query_params.get('month', now.month))
        data = ReportService.get_monthly_summary(year, month)
        summary = {k: float(v) for k, v in data['summary'].items()}
        reports = MonthlyReportSerializer(data['reports'], many=True).data
        return Response({'summary': summary, 'reports': reports})

    @action(detail=False, methods=['post'])
    def generate(self, request):
        now = timezone.now()
        year = int(request.data.get('year', now.year))
        month = int(request.data.get('month', now.month))
        reports = ReportService.generate_monthly_report(year, month)
        return Response({'generated': len(reports), 'year': year, 'month': month})
