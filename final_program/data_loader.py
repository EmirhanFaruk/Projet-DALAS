import pandas as pd
import joblib
from config import MODEL_FOLDER, STATION_COORDS_FILE, CLUSTER_FILE

# Load station and cluster data
stations_df = pd.read_csv(STATION_COORDS_FILE)
clusters_df = pd.read_csv(CLUSTER_FILE)

# Force into string
stations_df["station_code"] = stations_df["station_code"].astype(str)
clusters_df["station_code"] = clusters_df["station_code"].astype(str)

# Build mapping
station_to_cluster = dict(zip(clusters_df["station_code"], clusters_df["cluster"]))

# Load models
def load_models():
    models = {}
    for file in MODEL_FOLDER.glob("*.pkl"):
        try:
            loaded = joblib.load(file)

            # If it's just a scikit-learn model, wrap it in a dict
            if not isinstance(loaded, dict):
                # Extract info from filename
                fname = file.stem
                parts = fname.split("_")
                model_name = parts[0]
                cluster = int(parts[3])
                is_lagged = "lagged" in fname
                has_behavior_and_weather = "behavior+weather" in fname

                # For features, just reconstruct from filename
                features = ["sin_hour", "cos_hour", "is_weekend", "capacity"]
                if has_behavior_and_weather:
                    features += ["temperature","wind_speed","wind_direction","weather_code","is_day"]
                if is_lagged:
                    features += ["total_bikes_lag1","total_bikes_lag2"]

                loaded = {
                    "model": loaded,
                    "model_name": model_name,
                    "cluster": cluster,
                    "is_lagged": is_lagged,
                    "has_behavior_and_weather": has_behavior_and_weather,
                    "features": features
                }

            cluster_id = loaded["cluster"]
            models.setdefault(cluster_id, []).append(loaded)
        except Exception as e:
            print(f"Failed to load {file}: {e}")
    return models


MODELS = load_models()
