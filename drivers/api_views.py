from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Driver
from .serializers import DriverSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle_type', 'is_available']
    search_fields = ['name', 'phone', 'vehicle_number', 'license_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_destroy(self, instance):
        instance.soft_delete()
