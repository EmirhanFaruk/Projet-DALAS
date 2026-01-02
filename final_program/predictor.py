import pandas as pd
from datetime import datetime
from config import PREDICTION_LOG
from feature_builder import build_features
from request_data import fetch_weather
from data_loader import stations_df, station_to_cluster

def predict_station(station_code, model_entry, when):
    station = stations_df.loc[stations_df["station_code"]==station_code].iloc[0]
    cluster_id = station_to_cluster[station_code]

    weather = fetch_weather(station["latitude"], station["longitude"])
    features_dict = build_features(station, weather, when, model_entry["features"])

    X = pd.DataFrame([features_dict], columns=model_entry["features"])
    prediction = model_entry["model"].predict(X)[0]

    result = {
        "timestamp": datetime.now().isoformat(),
        "station_code": station_code,
        "cluster": cluster_id,
        "prediction": float(prediction),
        "features_used": model_entry["features"],
        "model": model_entry["model_name"]
    }

    # Log
    df = pd.DataFrame([result])
    if PREDICTION_LOG.exists():
        df.to_csv(PREDICTION_LOG, mode="a", header=False, index=False)
    else:
        df.to_csv(PREDICTION_LOG, index=False)

    return prediction
