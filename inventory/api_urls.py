from rest_framework.routers import DefaultRouter
from .api_views import InventoryViewSet

app_name = 'api-inventory'
router = DefaultRouter()
router.register('', InventoryViewSet, basename='inventory')
urlpatterns = router.urls
