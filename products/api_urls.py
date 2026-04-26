from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet

app_name = 'api-products'

router = DefaultRouter()
router.register('', ProductViewSet, basename='product')

urlpatterns = router.urls
