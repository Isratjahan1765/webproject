"""
Product API viewsets (DRF).
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer
from .services import ProductService


class ProductViewSet(viewsets.ModelViewSet):
    """
    Full CRUD API for Product Catalogue.
    
    list:   GET    /api/v1/products/
    create: POST   /api/v1/products/
    read:   GET    /api/v1/products/{id}/
    update: PUT    /api/v1/products/{id}/
    patch:  PATCH  /api/v1/products/{id}/
    delete: DELETE /api/v1/products/{id}/
    """
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit', 'is_active']
    search_fields = ['name', 'name_bn', 'sku', 'description']
    ordering_fields = ['name', 'unit_price', 'created_at', 'updated_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """GET /api/v1/products/low_stock/ — Products below minimum stock."""
        records = ProductService.get_low_stock_products()
        data = []
        for record in records:
            data.append({
                'product_id': record.product.id,
                'product_name': record.product.name,
                'sku': record.product.sku,
                'available_quantity': float(record.available_quantity),
                'minimum_stock': float(record.product.minimum_stock),
                'deficit': float(record.product.minimum_stock - record.available_quantity),
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """GET /api/v1/products/categories/ — List all categories."""
        from .models import ProductCategory
        return Response([
            {'value': c[0], 'label': c[1]} for c in ProductCategory.choices
        ])
