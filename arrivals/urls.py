from django.urls import path
from . import views

app_name = 'arrivals'

urlpatterns = [
    path('', views.ArrivalListView.as_view(), name='arrival-list'),
    path('<int:pk>/', views.ArrivalDetailView.as_view(), name='arrival-detail'),
    path('<int:pk>/confirm/', views.ArrivalConfirmView.as_view(), name='arrival-confirm'),
    path('<int:pk>/reject/', views.ArrivalRejectView.as_view(), name='arrival-reject'),
]
