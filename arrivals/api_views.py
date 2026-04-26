from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Arrival
from .serializers import ArrivalListSerializer, ArrivalDetailSerializer
from .services import ArrivalService


class ArrivalViewSet(viewsets.ModelViewSet):
    queryset = Arrival.objects.select_related('driver', 'confirmed_by').prefetch_related('items__product')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['batch_number', 'driver__name']
    ordering = ['-arrival_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ArrivalListSerializer
        return ArrivalDetailSerializer

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        try:
            arrival = ArrivalService.confirm_arrival(pk, request.user)
            return Response({'status': 'confirmed', 'batch': arrival.batch_number})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        reason = request.data.get('reason', '')
        try:
            arrival = ArrivalService.reject_arrival(pk, request.user, reason)
            return Response({'status': 'rejected', 'batch': arrival.batch_number})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
