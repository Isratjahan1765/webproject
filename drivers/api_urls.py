from rest_framework.routers import DefaultRouter
from .api_views import DriverViewSet

app_name = 'api-drivers'
router = DefaultRouter()
router.register('', DriverViewSet, basename='driver')
urlpatterns = router.urls
