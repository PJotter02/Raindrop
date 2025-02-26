from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
import requests
from .forms import WeatherForm


def fetch_weather(city, state, country):
    country = country.upper()

    # Validate country code before API call
    if len(country) != 2 or not country.isalpha():
        return {'error': 'Invalid country code. Use 2-letter ISO format (e.g., US, UK)'}

    # State only required for US locations
    location_query = f"{city},{state},{country}" if country == "US" else f"{city},{country}"

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": location_query,
                "units": "imperial",
                "appid": settings.OPENWEATHER_API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        if not all(key in data for key in ('main', 'weather', 'wind')):
            return {'error': 'Invalid API response format'}

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
        # Handle specific HTTP errors
        error_map = {
            401: "Invalid API key - contact site administrator",
            404: "Location not found - please check your input",
            429: "Too many requests - try again later"
        }
        return {'error': error_map.get(e.response.status_code, f"API Error: {e}")}
    except (KeyError, IndexError):
        return {'error': "Received unexpected data format from weather service"}
    except requests.exceptions.RequestException as e:
        return {'error': f"Connection error: {str(e)}"}


@require_http_methods(["GET", "POST"])
def weather_view(request):
    if request.method == 'POST':
        form = WeatherForm(request.POST)
        if form.is_valid():
            weather_data = fetch_weather(
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=form.cleaned_data['country']
            )
            if 'error' in weather_data:
                form.add_error(None, weather_data['error'])

            else:
                return render(request, 'weather_result.html', {
                    'weather_info': weather_data,
                    'form_data': form.cleaned_data
                })
    else:
        form = WeatherForm()

    return render(request, 'weather_form.html', {'form': form})
