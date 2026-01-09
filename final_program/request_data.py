import requests
import json
from datetime import datetime
import os


VELIB_URL = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&q=&rows=1500"
RETRIES = 3
RETRY_CODES = [
    429, # TOO_MANY_REQUESTS
    500, #  INTERNAL_SERVER_ERROR
    502, # BAD_GATEWAY,
    503, # SERVICE_UNAVAILABLE
    504, # GATEWAY_TIMEOUT
]

# https://api.open-meteo.com/v1/forecast?latitude=48.864716&longitude=2.349014&current=temperature_2m,is_day,wind_speed_10m,wind_direction_10m,weather_code

def fetch_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,is_day,wind_speed_10m,wind_direction_10m,weather_code"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        current = r.json()["current"]
        weather = {
            "timestamp": current.get("time"),
            "temperature": current.get("temperature_2m"),
            "is_day": current.get("is_day"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_direction": current.get("wind_direction_10m"),
            "weather_code": current.get("weather_code"),
        }
        return weather
    
    except Exception as e:
        print("Weather fetch failed:", e)
        return None
    
def fetch_velib_data(station_code):
    try:
        print("Fetching Velib data...", flush=True)
        r = requests.get(VELIB_URL)
        r.raise_for_status()
    except requests.HTTPError as e:
        if e.response.status_code in RETRY_CODES:
            for attempt in range(RETRIES):
                print(f"Retrying... ({attempt + 1}/{RETRIES})", flush=True)
                r = requests.get(VELIB_URL)
                if r.status_code not in RETRY_CODES:
                    break
            else:
                raise
        else:
            raise

    data = r.json()
    numbikes = -1
    for record in data['records']:
        fields = record['fields']
        if fields['stationcode'] == station_code:
            numbikes = fields['numbikesavailable']
            break

    return numbikes