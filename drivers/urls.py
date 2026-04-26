from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('', views.DriverListView.as_view(), name='driver-list'),
    path('create/', views.DriverCreateView.as_view(), name='driver-create'),
    path('<int:pk>/', views.DriverDetailView.as_view(), name='driver-detail'),
    path('<int:pk>/edit/', views.DriverUpdateView.as_view(), name='driver-update'),
    path('<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver-delete'),
]
