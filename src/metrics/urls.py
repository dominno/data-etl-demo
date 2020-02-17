from django.urls import path
from . import views

app_name = 'metrics'

urlpatterns = [
    path('', views.DashBoardView.as_view(), name='dashboard'),
    path('data/', views.metrics_data_json, name='data_json'),
]