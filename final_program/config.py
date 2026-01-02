from pathlib import Path

# Paths
DATA_FOLDER = Path("data")  # Path(../data)
MODEL_FOLDER = DATA_FOLDER / "04_models" / "trained_models"
CLUSTER_FILE = DATA_FOLDER / "03_clustering" / "station_clusters" / "station_clusters_kmeans_k2_feat_behavior+weather_rs42.csv"
STATION_COORDS_FILE = DATA_FOLDER / "02_features" / "station_coordinates" / "station_info.csv"
PREDICTION_LOG = DATA_FOLDER / "07_predictions" / "predictions.csv"

paths = [DATA_FOLDER, MODEL_FOLDER, CLUSTER_FILE, STATION_COORDS_FILE, PREDICTION_LOG]
for path in paths:
    path.parent.mkdir(parents=True, exist_ok=True)