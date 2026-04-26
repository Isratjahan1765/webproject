from rest_framework.routers import DefaultRouter
from .api_views import NotificationViewSet

app_name = 'api-notifications'
router = DefaultRouter()
router.register('', NotificationViewSet, basename='notification')
urlpatterns = router.urls
