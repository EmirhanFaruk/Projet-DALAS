# Predicting Vélib' Bike Availability in Paris

Can we predict how many Vélib' bikes a station will have in the next 15 minutes, and does the weather actually help?

This project builds a full data science pipeline: collecting our own dataset over ~50 days, cleaning it, clustering ~1,400 stations by usage behaviour, and training per-cluster regression models. Course project for **DALAS** (Data Science, Learning and Applications), M1 Computer Science, Sorbonne Université.

📄 **Full report:** [DALAS_Report.pdf](DALAS_Report.pdf)

## Key results

| Setting | Best model | R² | MAE (bikes) | RMSE |
|---|---|---|---|---|
| Cluster 0 (high-usage stations), with lag features | Random Forest | **0.970** | 1.17 | 2.08 |
| Cluster 1 (low-usage stations), with lag features | Random Forest | **0.944** | 0.95 | 1.68 |
| Cluster 0, without lag features | Random Forest | 0.383 | 7.47 | 9.41 |
| Cluster 1, without lag features | Random Forest | 0.181 | 4.84 | 6.43 |

Main findings:

- **Recent availability dominates.** Adding the availability 15 and 30 minutes earlier raises R² by more than 0.6 for every model.
- **Weather adds almost nothing** at short horizons, contrary to the usual assumption.
- **Simple models are enough.** Linear regression and SGD come within 0.005 R² of Random Forest once lag features are included.
- **Behaviour separates stations better than weather.** K-Means on behavioural features alone gives a silhouette score of 0.474 (k = 2), against 0.338 with weather features added.

## Data

We built the dataset ourselves from two public APIs:

| Source | Variables | Resolution |
|---|---|---|
| [Vélib' Open Data](https://www.velib-metropole.fr/donnees-open-data-gbfs-du-service-velib-metropole) | station, location, capacity, available bikes (mechanical / electric), free docks | 15–20 min |
| [Open-Meteo](https://open-meteo.com) | temperature, wind speed and direction, weather code, day/night | 15–20 min |

- Collected on a **Raspberry Pi 4B**, running continuously from 04/11/2025 to 23/12/2025 (~50 days).
- **4,048 JSON snapshots** (5.83 GB) merged into **6.07 million rows**.
- To respect the weather API rate limit, we query 86 reference points (20 Paris arrondissements + 66 communes) instead of ~1,500 stations, and assign each station to its nearest point.

## Pipeline

1. **Collection:** periodic snapshots of every station + weather, merged by nearest weather point, with a random 15–20 min delay.
2. **Cleaning:**
    - remove stations with capacity ≤ 1
    - remove rows where bikes > capacity (whole stations dropped above 10% corrupted rows)
    - aggregate duplicate station–timestamp pairs
    - drop sparse or frozen stations → **1,417 stations kept**
3. **Feature engineering:**
    - cyclic hour encoding (sin/cos), weekend flag
    - capacity and weather variables
    - lag features (bikes available at t−15 and t−30 min)
4. **Clustering:** K-Means on station-level behavioural features computed on the training split only, with k chosen by silhouette score.
5. **Modelling:** one model per cluster (Linear Regression, SGD Regressor, Random Forest), with a chronological 70 / 15 / 15 train / validation / test split to avoid temporal leakage.
6. **Evaluation:**
    - MAE, RMSE and R² per cluster and per configuration (with / without lags, with / without weather)
    - feature importance analysis

## Repository structure

| Folder | Content | Reads → writes (under `data/`) |
|---|---|---|
| `collect_data/` | `get_data.py`: one snapshot of all stations + weather, merged, then a 15–20 min wait | → `00_raw/` |
| `prepare_data/` | `prepare_data.ipynb`: JSON → CSV, cleaning, feature engineering, chronological split | `00_raw/` → `01_clean/`, `02_features/station_coordinates/` |
| `correlation_matrix/` | `correlation_matrix.ipynb`: correlation analysis | `00_raw/`, `01_clean/` → `05_visualization/` |
| `extract_features/` | `extract_station_features.ipynb`: station-level features for clustering | `01_clean/` → `02_features/` |
| `cluster_stations/` | `cluster_stations.ipynb`: K-Means + PCA | `02_features/` → `03_clustering/` |
| `train_models/` | `train_models_per_cluster.ipynb`: per-cluster training and evaluation | `01_clean/`, `03_clustering/` → `04_models/`, `06_statistics/` |
| `visualise_data/` | `visualise_data.ipynb`: missing-data analysis and result plots | `01_clean/`, `04_models/`, `06_statistics/` → `05_visualization/` |
| `source/` | Reference document (WMO weather code table) | |

## How to run

**Requirements:** Python 3.

```bash
pip install requests pandas numpy matplotlib seaborn folium scikit-learn joblib tqdm jupyter
```

All steps expect the `data/` folder at the repository root.

**1. Collect data (optional, only to gather new snapshots).** Run from inside `collect_data/`:

```bash
cd collect_data
python get_data.py
```

**2. Run the notebooks in this order.** Each one reads the outputs of the previous ones:

1. `prepare_data/prepare_data.ipynb`
2. `extract_features/extract_station_features.ipynb`
3. `cluster_stations/cluster_stations.ipynb`
4. `train_models/train_models_per_cluster.ipynb`

`correlation_matrix.ipynb` and `visualise_data.ipynb` are analysis-only. Run them after step 1 and step 4 respectively.

## Tech stack

Python · pandas · NumPy · scikit-learn · matplotlib · seaborn · folium · Raspberry Pi

## Authors

- Emirhan Faruk SAGIR
- Arafat ISLAM

Sorbonne Université, 2025–2026.

## License

MIT
