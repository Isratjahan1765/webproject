from django.urls import path
from . import views

app_name = 'revenue'
urlpatterns = [
    path('', views.RevenueListView.as_view(), name='revenue-list'),
]
