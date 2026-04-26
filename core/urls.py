from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard-api'),
]
