from rest_framework.routers import DefaultRouter
from .api_views import ArrivalViewSet

app_name = 'api-arrivals'
router = DefaultRouter()
router.register('', ArrivalViewSet, basename='arrival')
urlpatterns = router.urls
