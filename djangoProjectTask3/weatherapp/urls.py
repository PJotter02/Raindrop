# This file allows us to call our templates from views.py
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.weather_view), name='weather_view'),

    # User register, login, logout urls
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Favorite locations URLs
    path('favorites/', login_required(views.favorite_list), name='favorite_list'),
    path('favorites/add/', login_required(views.add_favorite_location), name='add_favorite_location'),
    path('favorites/remove/', login_required(views.remove_favorite_location), name='remove_favorite_location'),
]
