from rest_framework.routers import DefaultRouter
from .api_views import PickupViewSet

app_name = 'api-pickups'
router = DefaultRouter()
router.register('', PickupViewSet, basename='pickup')
urlpatterns = router.urls
