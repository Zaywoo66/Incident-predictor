# ml-pipeline/

Machine learning pipeline to predict infrastructure incidents based on Prometheus metrics.

## Components

- `features.py` — Reusable `FeatureEngineer` scikit-learn transformer for rolling time-series features (mean, std, lag, rate of change).
- `train.py` — Generates synthetic data if real data is missing, runs feature engineering, trains XGBoost classifier, and saves artifacts to `models/`.
- `evaluate.py` — Evaluates model on test set, generates `metrics/report.json` and a SHAP summary plot (`metrics/shap_summary.png`).

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model (uses synthetic data if metrics_labeled.csv is missing)
python train.py

# 3. Evaluate the model
python evaluate.py
```
