from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather_view, name='weather_view'),  # Changed name to match template references
]
