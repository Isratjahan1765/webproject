from django.urls import path
from .api_views import ProfileAPIView

app_name = 'api-accounts'
urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile'),
]
