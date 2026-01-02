import numpy as np

def build_features(station, weather, when, features_needed):
    hour = when.hour + when.minute / 60
    features_dict = {
        "sin_hour": np.sin(2 * np.pi * hour/24),
        "cos_hour": np.cos(2 * np.pi * hour/24),
        "is_weekend": int(when.weekday() >= 5),
        "capacity": station["capacity"],
    }

    if weather and any(f in features_needed for f in ["temperature","wind_speed","wind_direction","weather_code","is_day"]):
        features_dict.update({
            "temperature": weather["temperature_2m"],
            "wind_speed": weather["wind_speed_10m"],
            "wind_direction": weather["wind_direction_10m"],
            "weather_code": weather["weather_code"],
            "is_day": weather["is_day"],
        })

    if any(f in features_needed for f in ["total_bikes_lag1","total_bikes_lag2"]):
        # Placeholder for lag features
        features_dict.update({"total_bikes_lag1": 0, "total_bikes_lag2": 0})

    return [features_dict[f] for f in features_needed]
