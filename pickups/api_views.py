from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Pickup
from .serializers import PickupSerializer
from .services import PickupService


class PickupViewSet(viewsets.ModelViewSet):
    queryset = Pickup.objects.select_related('driver', 'confirmed_by').prefetch_related('items__product')
    serializer_class = PickupSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    ordering = ['-pickup_date']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        try:
            pickup = PickupService.confirm_pickup(pk, request.user)
            return Response({'status': 'confirmed', 'pickup': pickup.pickup_number})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reason = request.data.get('reason', '')
        try:
            pickup = PickupService.cancel_pickup(pk, request.user, reason)
            return Response({'status': 'cancelled', 'pickup': pickup.pickup_number})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
