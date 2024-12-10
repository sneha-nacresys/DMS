# In urls.py of your Django app

from django.urls import path
from . import views

urlpatterns = [
    path('RouteOptimizationView', views.RouteOptimizationView.as_view(), name='optimize_route'),
]
