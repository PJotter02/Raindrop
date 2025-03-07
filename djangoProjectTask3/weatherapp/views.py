# Import necessary Django and third-party modules
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
import requests
from .forms import WeatherForm


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

    # Validate country code format
    if len(country) != 2 or not country.isalpha():
        return {'error': 'Invalid country code. Use 2-letter ISO format (e.g., US, UK)'}

    # Construct location query based on whether it's a US location or not
    location_query = f"{city},{state},{country}" if country == "US" else f"{city},{country}"

    # OpenWeatherMap API configuration
    api_key = ''
    try:
        # Make API request with proper parameters
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": location_query,
                "units": "imperial",
                "appid": api_key
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Validate that response contains required data sections
        if any(key in data for key in ('main', 'weather', 'wind')):
            return {'error': 'Invalid API response format'}

        # Format and structure the weather data for template rendering
        return {
            'temperature': f"{data['main']['temp']}°F",
            'condition': data['weather'][0]['description'].title(),
            'icon': f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            'details': {
                'feels_like': f"{data['main']['feels_like']}°F",
                'humidity': f"{data['main']['humidity']}%",
                'wind_speed': f"{data['wind'].get('speed', 0)} mph",
                'pressure': f"{data['main']['pressure']} hPa"
            }
        }

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP error codes with user-friendly messages
        error_map = {
            401: "Invalid API key - contact site administrator",
            404: "Location not found - please check your input",
            429: "Too many requests - try again later"
        }
        return {'error': error_map.get(e.response.status_code, f"API Error: {e}")}
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
    if request.method == 'POST':
        print("Post was successful")
        form = WeatherForm(request.POST)
        if form.is_valid():
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
                    'weather_info': weather_data,
                    'form_data': form.cleaned_data
                })
    else:
        # For GET requests, display empty form
        form = WeatherForm()

    # Render form page (either fresh or with errors)
    return render(request, 'weather_form.html', {'form': form})
