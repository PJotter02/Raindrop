from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # Includes login, logout, password reset
    path('', include('weatherapp.urls')),  # Include your app's URLs
]
