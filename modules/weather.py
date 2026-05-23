# ============================================
# Weather Module
# Gets weather data from OpenWeatherMap API
# FREE API key available at openweathermap.org
# ============================================

import requests
import os

def get_weather(city="Lahore"):
    api_key = os.getenv("WEATHER_API_KEY", "")

    # If no API key, return a friendly message
    if not api_key or api_key == "your_key_here":
        return (
            f"Weather feature ke liye free API key chahiye!\n"
            f"1. Jao: openweathermap.org\n"
            f"2. Free account banao\n"
            f"3. API key copy karo\n"
            f"4. .env file mein WEATHER_API_KEY=yourkey likh do\n"
            f"Phir restart karo Jarvis ko!"
        )

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",  # Celsius
            "lang": "en"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code == 200:
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind = data["wind"]["speed"]

            return (
                f"🌤️ {city} ka mausam:\n"
                f"Temperature: {temp}°C (feels like {feels}°C)\n"
                f"Halaat: {description}\n"
                f"Humidity: {humidity}%\n"
                f"Hawa: {wind} m/s"
            )
        else:
            return f"Weather nahi mila '{city}' ka. City ka naam check karo."

    except requests.exceptions.ConnectionError:
        return "Internet connection nahi hai. Weather nahi aa sakta abhi."
    except Exception as e:
        return f"Weather fetch karne mein error: {str(e)}"
