from django.urls import path, include

urlpatterns = [
    path('', include('weatherapp.urls')),  # Include app URLs here
]
