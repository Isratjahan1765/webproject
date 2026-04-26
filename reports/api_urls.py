from rest_framework.routers import DefaultRouter
from .api_views import ReportViewSet

app_name = 'api-reports'
router = DefaultRouter()
router.register('', ReportViewSet, basename='report')
urlpatterns = router.urls
