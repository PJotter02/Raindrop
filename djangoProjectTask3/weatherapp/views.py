import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .forms import WeatherForm

def fetch_weather(city, state, country):
    search_query = f"{city} {state} {country} weather"
    url = f"https://www.google.com/search?q={search_query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        temperature_f = soup.find("span", class_="wob_t")

        if temperature_f:  # Check if temperature_f is not None
            try:
                temp_f = int(temperature_f.text)
            except (ValueError, AttributeError):
                temp_f = None  # Handle cases where temperature is not a valid integer
        else:
            temp_f = None

        if temp_f is not None:
            temp_c = round((temp_f - 32) * (5 / 9), 1)
            temperature_c = f"{temp_c}"
        else:
            temperature_c = 'N/A'

        conditions = soup.find("span", {"id": "wob_dc"})
        location = soup.find("div", {"id": "wob_loc"})
        precipitation = soup.find("span", {"id": "wob_pp"})
        humidity = soup.find("span", {"id": "wob_hm"})
        wind = soup.find("span", {"id": "wob_ws"})

        weather_info = {
            'temperature_f': f"{temp_f}°F" if temp_f is not None else 'N/A',  # Display N/A if temp_f is None
            'temperature_c': temperature_c,
            'conditions': conditions.text if conditions else 'N/A',
            'location': location.text if location else 'N/A',
            'precipitation': precipitation.text if precipitation else 'N/A',
            'humidity': humidity.text if humidity else 'N/A',
            'wind': wind.text if wind else 'N/A'
        }
        return weather_info
    except requests.exceptions.RequestException as e:
        # Handle network errors
        print(f"Network error: {e}")  # Log the error for debugging
        return None  # Or return a dictionary with an error message
    except Exception as e:
        # Handle other potential errors during parsing
        print(f"An error occurred: {e}")
        return None  #Or return a dictionary with an error message


def weather_view(request):
    if request.method == 'POST':
        form = WeatherForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['firstName']
            last_name = form.cleaned_data['lastName']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']

            weather_info = fetch_weather(city, state, country)

            # Handle the case where fetch_weather returns None (error)
            if weather_info is None:
                return render(request, 'weather_result.html', {
                    'error_message': 'Could not retrieve weather information.  Please check the location and try again.'
                })

            return render(request, 'weather_result.html', {
                'first_name': first_name,
                'last_name': last_name,
                'city': city,
                'state': state,
                'country': country,
                'weather_info': weather_info
            })
    else:
        form = WeatherForm()

    return render(request, 'weather_form.html', {'form': form})
