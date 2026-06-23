"""
URL configuration for the DbAgent web interface.
"""
from django.urls import path

from . import views

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    # API endpoints
    path('api/query', views.api_query, name='api_query'),
    path('api/status', views.api_status, name='api_status'),
    path('api/pull-model', views.api_pull_model, name='api_pull_model'),
]