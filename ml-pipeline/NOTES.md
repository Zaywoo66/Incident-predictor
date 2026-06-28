# ml-pipeline/ — Notes

## Deviations from contract

- Used a scikit-learn compatible `FeatureEngineer` class with pandas rolling operations instead of the `tsfresh` library. `tsfresh` is powerful but typically used for extracting hundreds of features from grouped series, whereas the contract only strictly requested basic rolling time-series features (mean, std, lag, rate of change). This approach is lighter, easier to serialize, and faster for inference.
- Added synthetic data generation in `train.py` as a fallback when `data/raw/metrics_labeled.csv` is not present, allowing pipeline development without a full infrastructure run.

## Design decisions

- `features.py` exports a `FeatureEngineer` transformer. This makes sure that the exact same feature logic and state (window sizes, etc.) are loaded directly into the API endpoint (`api/main.py`) using `joblib.load`.
- The evaluation script calculates classification metrics and saves them to `report.json` as requested. It also triggers a warning if `recall < 0.5`, to guard against models that naively predict the majority class.
- The train/test split is done chronologically (first 80% train, last 20% test) to prevent data leakage in time series forecasting.
