from pathlib import Path

# Paths
DATA_FOLDER = Path("data")  # Path(../data)

MODEL_FOLDER = DATA_FOLDER / "04_models" / "trained_models"
MODEL_FULL_LAGGED_FILE = MODEL_FOLDER / "model_k2_feat_behavior+weather_lagged_rs42.pkl"
MODEL_BEH_LAGGED_FILE = MODEL_FOLDER / "model_k2_feat_behavior_lagged_rs42.pkl"
MODEL_FULL_NOT_LAGGED_FILE = MODEL_FOLDER / "model_k2_feat_behavior+weather_not_lagged_rs42.pkl"
MODEL_BEH_NOT_LAGGED_FILE = MODEL_FOLDER / "model_k2_feat_behavior_not_lagged_rs42.pkl"

CLUSTER_FOLDER = DATA_FOLDER / "03_clustering" / "station_clusters"
CLUSTER_FULL_FILE = CLUSTER_FOLDER / "station_clusters_kmeans_k2_feat_behavior+weather_rs42.csv"
CLUSTER_BEH_FILE = CLUSTER_FOLDER / "station_clusters_kmeans_k2_feat_behavior_rs42.csv"


STATION_INFO_FILE = DATA_FOLDER / "02_features" / "station_coordinates" / "station_info.csv"

PREDICTION_FOLDER = DATA_FOLDER / "07_predictions"
PREDICTION_LOG = PREDICTION_FOLDER / "predictions.csv"

paths = [DATA_FOLDER, MODEL_FOLDER, CLUSTER_FOLDER, PREDICTION_FOLDER]
for path in paths:
    path.parent.mkdir(parents=True, exist_ok=True)