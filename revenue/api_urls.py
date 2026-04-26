from rest_framework.routers import DefaultRouter
from .api_views import RevenueViewSet

app_name = 'api-revenue'
router = DefaultRouter()
router.register('', RevenueViewSet, basename='revenue')
urlpatterns = router.urls
