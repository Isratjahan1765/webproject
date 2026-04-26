from django.urls import path
from . import views

app_name = 'pickups'
urlpatterns = [
    path('', views.PickupListView.as_view(), name='pickup-list'),
    path('<int:pk>/', views.PickupDetailView.as_view(), name='pickup-detail'),
    path('<int:pk>/confirm/', views.PickupConfirmView.as_view(), name='pickup-confirm'),
    path('<int:pk>/cancel/', views.PickupCancelView.as_view(), name='pickup-cancel'),
]
