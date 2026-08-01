import requests

def get_coordinates(city, country):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    if not data.get("results"):
        return None
    result = data["results"][0]
    return {"lat": result["latitude"], "lon": result["longitude"]}

def get_weather(city, country):
    coords = get_coordinates(city, country)
    if not coords:
        return {"temperature": None, "condition": "Unknown", "season": "All Season"}

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": "temperature_2m,relative_humidity_2m,precipitation",
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json().get("current", {})

    temp = data.get("temperature_2m")
    humidity = data.get("relative_humidity_2m")
    rain = data.get("precipitation", 0)

    if temp is None:
        season = "All Season"
    elif temp >= 28:
        season = "Hot"
    elif temp >= 18:
        season = "Mild"
    else:
        season = "Cold"

    return {
        "temperature": temp,
        "humidity": humidity,
        "rain": rain > 0,
        "season": season,
    }