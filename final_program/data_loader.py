import pandas as pd
import joblib
import os
from config import MODEL_FOLDER, STATION_INFO_FILE, CLUSTER_FILE

# Load station and cluster data
stations_df = pd.read_csv(STATION_INFO_FILE)
clusters_df = pd.read_csv(CLUSTER_FILE)

# Force into string
stations_df["station_code"] = stations_df["station_code"].astype(str)
clusters_df["station_code"] = clusters_df["station_code"].astype(str)

# Build mapping
station_to_cluster = dict(zip(clusters_df["station_code"], clusters_df["cluster"]))

def get_is_lagged(filename):
    return "not_lagged" not in filename

def get_has_behavior_weather(filename):
    return "behavior+weather" in filename

def get_features(filename):
    features = [
        # Time
        "sin_hour",
        "cos_hour",
        "is_weekend",

        # Station context
        "capacity"
    ]

    if get_has_behavior_weather(filename):
        features = features + [
                                # Weather
                                "temperature",
                                "wind_speed",
                                "wind_direction",
                                "weather_code",
                                "is_day",
                            ]
        
    if get_is_lagged(filename):
        features = features + [
                                # Bike lag
                                "total_bikes_lag1", 
                                "total_bikes_lag2"
                            ]
    return features


# Load models
def load_models():
    # LOAD THE MODELS
    pred_models = {}

    extension_tags = [
        f"feat_{fn}_lag_{lname}_rs{rs}_k{k}" 
        for fn in ["behavior+weather", "behavior"]
        for lname in ["lagged", "not_lagged"]
        for rs in [42]#[42, 72]
        for k in [2]
    ]

    for cluster_id in range(2):
        pred_models[cluster_id] = {}
        for model_name in ["LinearRegression", "SGDRegressor", "RandomForest"]:
            pred_models[cluster_id][model_name] = []
            for extension_tag in extension_tags:
                filename = f"{MODEL_FOLDER}/{model_name}_model_cluster_{cluster_id}_{extension_tag}.pkl"
                if os.path.exists(filename):
                    pred_models[cluster_id][model_name].append({
                        "model": joblib.load(filename),
                        "is_lagged": get_is_lagged(filename),
                        "has_behavior_and_weather": get_has_behavior_weather(filename),
                        "features": get_features(extension_tag)
                        })
                    
                    print(f"Loaded: {filename}")
                else:
                    print(f"File not found: {filename}")
    return pred_models


MODELS = load_models()
