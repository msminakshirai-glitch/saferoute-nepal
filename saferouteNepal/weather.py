import requests

def get_rainfall(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum",
        "timezone": "Asia/Kathmandu",
        "past_days": 1,
        "forecast_days": 1
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        rainfall = data["daily"]["precipitation_sum"][0]
        if rainfall is None:
            return 0
        return round(rainfall, 1)
    except Exception as e:
        print(f"Could not fetch weather data: {e}")
        return 0


def get_rainfall_forecast(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum",
        "timezone": "Asia/Kathmandu",
        "forecast_days": 3
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        forecasts = data["daily"]["precipitation_sum"]
        forecasts = [f if f is not None else 0 for f in forecasts]
        return [round(f, 1) for f in forecasts]
    except Exception as e:
        print(f"Could not fetch forecast: {e}")
        return [0, 0, 0]
