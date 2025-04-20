<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from .models import SearchHistory, FavoriteLocation
=======
# Import necessary Django and third-party modules
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
import requests
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c
from .forms import WeatherForm
from django.conf import settings
import requests
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from django.core.cache import cache
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.http import require_http_methods

# Configure logging
logger = logging.getLogger(__name__)

# Cache settings
GEOCODE_CACHE_TIMEOUT = 60 * 60 * 24
SAFE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"


def sanitize_cache_key(key):
    return "".join(c if c in SAFE_CHARS else "_" for c in key)


def get_coordinates(city, state, country):
    raw_key = f"geo_{city}_{state}_{country}"
    cache_key = sanitize_cache_key(raw_key)

    cached = cache.get(cache_key)
    if cached:
        return cached

    geolocator = Nominatim(user_agent="weather_app_uccs_project")
    location_str = f"{city}, {state}, {country}" if country == "US" else f"{city},{country}"

    try:
        location = geolocator.geocode(
            location_str,
            exactly_one=True,
            timeout=10,
            language="en",
            addressdetails=True
        )
        if location:
            coords = (location.latitude, location.longitude)
            cache.set(cache_key, coords, GEOCODE_CACHE_TIMEOUT)
            return coords
        logger.warning(f"Geocoding failed for: {location_str}")
        return (None, None)
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        logger.error(f"Geocoding error: {str(e)}")
        return (None, None)


def validate_owm_response(data, required_fields):
    return all(field in data for field in required_fields)


def fetch_weather(city, state, country):
    """
    Fetches weather data from OpenWeatherMap API for a given location.
    Parameters:
        city (str): Name of the city
        state (str): State code (required for US locations)
        country (str): Two-letter country code
    Returns:
        dict: Weather data or error message
    """
    country = country.upper()
<<<<<<< HEAD
    if len(country) != 2 or not country.isalpha():
        return {'error': 'Invalid country code. Use 2-letter ISO format (e.g., US, UK)'}

=======

    # Validate country code format
    if len(country) != 2 or not country.isalpha():
        return {'error': 'Invalid country code. Use 2-letter ISO format (e.g., US, UK)'}

    # Construct location query based on whether it's a US location or not
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c
    location_query = f"{city},{state},{country}" if country == "US" else f"{city},{country}"
    api_key = settings.OPENWEATHER_API_KEY

    endpoints = {
        'current': "https://api.openweathermap.org/data/2.5/weather",
        'forecast': "https://api.openweathermap.org/data/2.5/forecast"
    }

<<<<<<< HEAD
    try:
        current_response = requests.get(
            endpoints['current'],
=======
    # OpenWeatherMap API configuration
    api_key = ''
    try:
        # Make API request with proper parameters
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c
            params={
                "q": location_query,
                "units": "imperial",
                "appid": api_key
            },
            timeout=15
        )
        current_response.raise_for_status()
        current_data = current_response.json()

<<<<<<< HEAD
        if not validate_owm_response(current_data, ['main', 'weather', 'wind']):
            logger.error(f"Invalid current weather structure: {current_data.keys()}")
            return {'error': 'Invalid weather data format'}

        forecast_response = requests.get(
            endpoints['forecast'],
            params={
                "q": location_query,
                "units": "imperial",
                "appid": api_key
            },
            timeout=15
        )
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        if 'list' not in forecast_data:
            logger.error(f"Invalid forecast structure: {forecast_data.keys()}")
            return {'error': 'Invalid forecast data'}

        forecast = []
        for entry in forecast_data['list'][::8]:
            try:
                date_str = entry['dt_txt']
                date_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                forecast.append({
                    'date': date_object,
                    'temp': f"{entry['main']['temp']}°F",
                    'icon': f"https://openweathermap.org/img/wn/{entry['weather'][0]['icon']}@2x.png",
                    'description': entry['weather'][0]['description'].title(),
                    'humidity': f"{entry['main']['humidity']}%",
                    'wind_speed': f"{entry['wind']['speed']} mph"
                })
            except (KeyError, IndexError, ValueError) as e:
                logger.warning(f"Forecast processing error: {str(e)}")
                continue
=======
        # Validate that response contains required data sections
        if any(key in data for key in ('main', 'weather', 'wind')):
            return {'error': 'Invalid API response format'}
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c

        # Format and structure the weather data for template rendering
        return {
            'current': {
                'temperature': f"{current_data['main']['temp']}°F",
                'condition': current_data['weather'][0]['description'].title(),
                'icon': f"https://openweathermap.org/img/wn/{current_data['weather'][0]['icon']}@2x.png",
                'details': {
                    'feels_like': f"{current_data['main']['feels_like']}°F",
                    'humidity': f"{current_data['main']['humidity']}%",
                    'wind_speed': f"{current_data['wind'].get('speed', 0)} mph",
                    'pressure': f"{current_data['main']['pressure']} hPa"
                }
            },
            'forecast': forecast
        }

    except requests.exceptions.HTTPError as e:
<<<<<<< HEAD
=======
        # Handle specific HTTP error codes with user-friendly messages
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c
        error_map = {
            401: "Invalid API key - contact administrator",
            404: "Location not found - check input",
            429: "Too many requests - try again later"
        }
        logger.error(f"API HTTP error: {e.response.status_code}")
        return {'error': error_map.get(e.response.status_code, f"API Error: {e}")}
<<<<<<< HEAD
    except (KeyError, IndexError) as e:
        logger.error(f"Data parsing error: {str(e)}")
        return {'error': "Unexpected data format from service"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        return {'error': f"Connection error: {str(e)}"}


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('weather_view')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("weather_view")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def weather_view(request):
    context = {
        'recent_searches': request.user.searches.all().order_by('-search_date')[:5],
        'favorites': request.user.favorites.all().order_by('-created_at')
    }  # Initialize context
    if request.method == 'GET' and 'city' in request.GET:
        # Extract query parameters from GET request
        city = request.GET.get('city')
        state = request.GET.get('state', '')  # Optional
        country = request.GET.get('country', '')

        # Validate required fields
        if not city or not country:
            return HttpResponseBadRequest("Invalid search parameters.")

        # Pre-fill form with existing data
        initial_data = {'city': city, 'state': state, 'country': country}
        form = WeatherForm(initial=initial_data)

        # Fetch weather data
        weather_data = fetch_weather(city, state, country)
        if 'error' in weather_data:
            form.add_error(None, weather_data['error'])
            context['form'] = form
            context['recent_searches'] = request.user.searches.all().order_by('-search_date')[:5]
            context['weather_info'] = weather_data
            context['favorites'] = request.user.favorites.all().order_by('-created_at')
            return render(request, 'weatherapp/weather_form.html', context)
        else:
            form = WeatherForm(initial=initial_data)
            # Save to search history
            lat, lon = get_coordinates(city, state, country)
            # SearchHistory.objects.create( #Remove this because you don't want to keep creating it
            #     user=request.user,
            #     city=city,
            #     state=state,
            #     country=country,
            #     coordinates=f"{lat},{lon}",
            #     query=f"{city}, {state}, {country}"
            # )
            is_favorite = FavoriteLocation.objects.filter(
                user=request.user,
                city=city,
                state=state,
                country=country
            ).exists()

            context = {
                'weather_info': weather_data,
                'form_data': initial_data,
                'is_favorite': is_favorite,
                'favorites': request.user.favorites.all().order_by('-created_at'),
                'map_context': {
                    'api_key': settings.OPENWEATHER_API_KEY,
                    'lat': lat,
                    'lon': lon
                }
            }

            return render(request, 'weatherapp/weather_result.html', context)

=======
    except (KeyError, IndexError):
        # Handle malformed API response data
        return {'error': "Received unexpected data format from weather service"}
    except requests.exceptions.RequestException as e:
        # Handle general request errors (timeout, connection issues, etc.)
        return {'error': f"Connection error: {str(e)}"}


@require_http_methods(["GET", "POST"])
def weather_view(request):
    """
    View function to handle weather form submission and display.
    Supports both GET (display form) and POST (process form) requests.
    """
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c
    if request.method == 'POST':
        form = WeatherForm(request.POST)
        if form.is_valid():
<<<<<<< HEAD
            # Get form data
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']

            # Fetch weather data
            weather_data = fetch_weather(city, state, country)

            if 'error' in weather_data:
                form.add_error(None, weather_data['error'])
                context['form'] = form
                context['recent_searches'] = request.user.searches.all().order_by('-search_date')[:5]
                context['favorites'] = request.user.favorites.all().order_by('-created_at')
                return render(request, 'weatherapp/weather_form.html', context)
            else:
                # Get coordinates
                lat, lon = get_coordinates(city, state, country)

                # Create search history entry
                SearchHistory.objects.create(
                    user=request.user,
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    country=form.cleaned_data['country'],
                    coordinates=f"{lat},{lon}",
                    query=f"{city}, {state}, {country}"  # Optional, auto-populated
                )

                # Fallback coordinates
                if None in (lat, lon):
                    lat, lon = 38.8339, -104.8214
                    logger.info(f"Using fallback coordinates for {city}")

                is_favorite = FavoriteLocation.objects.filter(
                    user=request.user,
                    city=city,
                    state=state,
                    country=country
                ).exists()

                context = {
=======
            print("Form is valid")
            # Fetch weather data using form inputs
            weather_data = fetch_weather(
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=form.cleaned_data['country']
            )
            # Handle any errors from the weather fetch
            if 'error' in weather_data:
                form.add_error(None, weather_data['error'])
            else:
                # Render results page with weather data
                return render(request, 'weather_result.html', {
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c
                    'weather_info': weather_data,
                    'form_data': form.cleaned_data,
                    'map_context': {
                        'api_key': settings.OPENWEATHER_API_KEY,
                        'lat': lat,
                        'lon': lon
                    },
                    'is_favorite': is_favorite,
                    'favorites': request.user.favorites.all().order_by('-created_at')
                }

                return render(request, 'weatherapp/weather_result.html', context)
    else:
        # For GET requests, display empty form
        form = WeatherForm()
        context['form'] = form

<<<<<<< HEAD
    # Add recent searches to context
    context['recent_searches'] = request.user.searches.all().order_by('-search_date')[:5]
    context['favorites'] = request.user.favorites.all().order_by('-created_at')
    return render(request, 'weatherapp/weather_form.html', context)


@login_required
@require_http_methods(["POST"])
def add_favorite_location(request):
    city = request.POST.get('city')
    state = request.POST.get('state')
    country = request.POST.get('country')
    nickname = request.POST.get('nickname', '')  # Optional nickname

    if not all([city, country]):
        return JsonResponse({'status': 'error', 'message': 'City and country are required.'}, status=400)

    # Check if a favorite location with the same details already exists for the user
    existing_favorite = FavoriteLocation.objects.filter(
        user=request.user,
        city=city,
        state=state,
        country=country
    ).first()

    if existing_favorite:
        return JsonResponse({'status': 'error', 'message': 'Location is already a favorite.'}, status=400)

    lat, lon = get_coordinates(city, state, country)
    if not lat or not lon:
        return JsonResponse({'status': 'error', 'message': 'Could not retrieve coordinates.'}, status=400)

    try:
        FavoriteLocation.objects.create(
            user=request.user,
            city=city,
            state=state,
            country=country,
            coordinates=f"{lat},{lon}",
            nickname=nickname
        )
        return JsonResponse({'status': 'success', 'message': f'{city} added to favorites.', 'action': 'remove'})
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        return JsonResponse({'status': 'error', 'message': 'Could not add to favorites.'}, status=500)


@login_required
@require_http_methods(["POST"])
def remove_favorite_location(request):
    city = request.POST.get('city')
    state = request.POST.get('state')
    country = request.POST.get('country')

    if not all([city, country]):
        return JsonResponse({'status': 'error', 'message': 'City and country are required.'}, status=400)

    try:
        location = FavoriteLocation.objects.get(user=request.user, city=city, state=state, country=country)
        location.delete()
        return JsonResponse({'status': 'success', 'message': f'{city} removed from favorites.', 'action': 'add'})
    except FavoriteLocation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Location not found in favorites.'}, status=404)
    except Exception as e:
        logger.error(f"Error removing favorite: {e}")
        return JsonResponse({'status': 'error', 'message': 'Could not remove from favorites.'}, status=500)


@login_required
def favorite_list(request):
    favorites = request.user.favorites.all()
    return render(request, 'weatherapp/favorite_list.html', {'favorites': favorites})
=======
    # Render form page (either fresh or with errors)
    return render(request, 'weather_form.html', {'form': form})
>>>>>>> cea6acda02bde970895e2d52b45b11b4ec9f796c
