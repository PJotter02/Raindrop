from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # Automatically manages ChromeDriver
from django.shortcuts import render
from .forms import WeatherForm
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def fetch_weather(city, state, country):
    # Set up Selenium WebDriver with WebDriver Manager
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")

    # Enable the acceptInsecureCerts capability
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptInsecureCerts'] = True

    # Use WebDriver Manager to automatically download and manage the correct ChromeDriver version
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.execute_cdp_cmd("Security.setIgnoreCertificateErrors", {"ignore": True})

        # Build the URL for Wunderground
        url = f"https://www.wunderground.com/weather/{country}/{state}/{city}"
        driver.get(url)

        # Use WebDriverWait to dynamically wait for elements to load
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements

        # Scrape temperature (Fahrenheit)
        try:
            temperature_f = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "wu-value"))
            ).text
        except Exception:
            temperature_f = "N/A"

        # Scrape weather condition (e.g., Cloudy)
        try:
            condition = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "condition-icon"))
            ).text
        except Exception:
            condition = "N/A"

        # Scrape wind information
        try:
            wind = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'Wind')]/following-sibling::span")
                )
            ).text
        except Exception:
            wind = "N/A"

        # Scrape humidity
        try:
            humidity = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'Humidity')]/following-sibling::span")
                )
            ).text
        except Exception:
            humidity = "N/A"

        # Return the scraped data as a dictionary
        weather_info = {
            'temperature_f': temperature_f,
            'condition': condition,
            'wind': wind,
            'humidity': humidity,
        }
        return weather_info

    except Exception as e:
        print(f"Error during scraping: {e}")
        return {'error': 'Failed to fetch weather data. Please try again later.'}

    finally:
        driver.quit()


def weather_view(request):
    if request.method == 'POST':
        print("POST request received!")
        form = WeatherForm(request.POST)
        if form.is_valid():
            print("Form is valid!")
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']

            # Fetch weather data (replace with your actual logic)
            weather_info = fetch_weather(city, state, country)

            # Render the results page with weather data
            return render(request, 'weather_result.html', {
                'city': city,
                'state': state,
                'country': country,
                'weather_info': weather_info,
            })
        else:
            print("Form is invalid!")
    else:
        print("GET request received!")
        form = WeatherForm()

    return render(request, 'weather_form.html', {'form': form})
