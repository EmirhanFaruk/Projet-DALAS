import json
import os
from datetime import datetime
from math import sqrt
import random
import time

from get_velib_data import fetch_velib_data
from get_weather_data import fetch_weather_for_points, PARIS_ARRONDISSEMENTS


MAX_INTERVAL = 20 * 60  # 20 minutes in seconds
MIN_INTERVAL = 15 * 60  # 15 minutes in seconds



def correlate_coords(velib_stations, weather_data):
    correlated = []
    weather_dict = {(entry["latitude"], entry["longitude"]): entry["weather"] for entry in weather_data}

    for station in velib_stations:
        lat, lon = station["fields"].get("coordonnees_geo", (None, None))
        if lat is not None and lon is not None:
            weather = weather_dict.get((lat, lon), {})
            correlated.append({
                "station": station,
                "weather": weather
            })
    return correlated

def distance(lat1, lon1, lat2, lon2):
    return sqrt(((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2))

def correlate_coords(velib_stations, weather_data):
    # Build a lookup table for weather by arrondissement/commune
    weather_lookup = {w["arrondissement"]: w for w in weather_data}

    correlated = []
    for station in velib_stations:
        commune = station["fields"].get("nom_arrondissement_communes")
        lat, lon = station["fields"].get("coordonnees_geo", (None, None))

        if commune == "Paris" and lat is not None and lon is not None:
            # Find closest arrondissement
            min_dist = float("inf")
            closest_arr = None
            for arr_lat, arr_lon, arr_name in PARIS_ARRONDISSEMENTS:
                dist = distance(lat, lon, arr_lat, arr_lon)
                if dist < min_dist:
                    min_dist = dist
                    closest_arr = arr_name
            weather = weather_lookup.get(closest_arr, {}).get("weather", {})
        else:
            weather = weather_lookup.get(commune, {}).get("weather", {})

        merged = station.copy()
        merged["weather"] = weather
        correlated.append(merged)

    return correlated
    

def get_data():
    _, velib_stations = fetch_velib_data()
    _, weather_data = fetch_weather_for_points()
    
    correlated_coords = correlate_coords(velib_stations, weather_data)
    
    # saving correlated data
    correlated_folder = "correlated_data_json"
    os.makedirs(correlated_folder, exist_ok=True)
    correlated_filename = os.path.join(correlated_folder, f"correlated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(correlated_filename, "w", encoding="utf-8") as f:
        json.dump(correlated_coords, f, ensure_ascii=False, indent=2)

    print(f"Saved correlated data for {len(correlated_coords)} stations to {correlated_filename}.")

def get_data_loop():
    start_time = time.time()
    
    try:
        get_data()
    except Exception as e:
        print(f"Error during get_data(): {e}")

    elapsed = time.time() - start_time
    wait_time = random.randint(MIN_INTERVAL, MAX_INTERVAL) - elapsed
    if wait_time < 0:
        wait_time = 0  # if processing took longer than interval, start next immediately

    print(f"Waiting {wait_time:.2f} seconds until next fetch...")
    time.sleep(wait_time)

if __name__ == "__main__":
    get_data_loop()