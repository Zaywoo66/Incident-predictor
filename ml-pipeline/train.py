import os
import argparse
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
from features import FeatureEngineer

def generate_synthetic_data(num_rows=1000) -> pd.DataFrame:
    """Generate synthetic data matching the schema if real data is missing."""
    np.random.seed(42)
    timestamps = pd.date_range(start="2026-01-01", periods=num_rows, freq="15s")
    
    data = {
        "timestamp": timestamps,
        "cpu": np.random.uniform(10, 60, num_rows),
        "ram": np.random.uniform(20, 70, num_rows),
        "latency": np.random.uniform(0.01, 0.05, num_rows),
        "disk_io": np.random.uniform(100, 1000, num_rows),
        "network_io": np.random.uniform(100, 1000, num_rows),
        "deploy_flag": np.random.choice([0, 1], p=[0.95, 0.05], size=num_rows),
        "incident_label": np.zeros(num_rows, dtype=int)
    }
    
    # Introduce some incidents (high cpu/ram/latency)
    incident_indices = np.random.choice(num_rows, int(num_rows * 0.2), replace=False)
    data["incident_label"][incident_indices] = 1
    
    # Modify metrics for incidents to give the model something to learn
    data["cpu"][incident_indices] = np.random.uniform(70, 100, len(incident_indices))
    data["ram"][incident_indices] = np.random.uniform(70, 95, len(incident_indices))
    data["latency"][incident_indices] = np.random.uniform(0.1, 0.5, len(incident_indices))
    
    return pd.DataFrame(data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="../data/raw/metrics_labeled.csv", help="Path to input data")
    parser.add_argument("--models-dir", default="models", help="Directory to save models")
    args = parser.parse_args()
    
    if os.path.exists(args.data):
        print(f"[*] Loading data from {args.data}")
        df = pd.read_csv(args.data)
        # Sort by timestamp just in case
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp").reset_index(drop=True)
    else:
        print(f"[*] Data file {args.data} not found. Generating synthetic dataset for development.")
        df = generate_synthetic_data()
        
    print(f"[*] Total rows: {len(df)}")
    print(f"[*] Incident distribution:\n{df['incident_label'].value_counts(normalize=True)}")
    
    # 1. Feature Engineering
    print("[*] Running feature engineering...")
    fe = FeatureEngineer(window_size=5)
    
    # Fit and transform
    X = fe.fit_transform(df)
    
    # Separate target
    y = X["incident_label"]
    X = X.drop(columns=["incident_label"])
    
    # Train/test split (chronological split is better for time series)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"[*] Training data shape: {X_train.shape}")
    
    # 2. Train XGBoost
    print("[*] Training XGBoost model...")
    # Deal with class imbalance dynamically
    scale_pos_weight = (len(y_train) - y_train.sum()) / max(y_train.sum(), 1)
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="logloss"
    )
    
    model.fit(X_train, y_train)
    
    # 3. Save artifacts
    os.makedirs(args.models_dir, exist_ok=True)
    
    pipeline_path = os.path.join(args.models_dir, "feature_pipeline.pkl")
    model_path = os.path.join(args.models_dir, "model.pkl")
    
    joblib.dump(fe, pipeline_path)
    joblib.dump(model, model_path)
    
    print(f"[*] Saved feature pipeline to {pipeline_path}")
    print(f"[*] Saved model to {model_path}")
    
    # Save test set for evaluate.py
    test_data_path = "test_data.csv"
    test_df = X_test.copy()
    test_df["incident_label"] = y_test
    test_df.to_csv(test_data_path, index=False)
    print(f"[*] Saved test set to {test_data_path} for evaluation")

if __name__ == "__main__":
    main()
