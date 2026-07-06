import os
import argparse
import joblib
import pandas as pd
from features import FeatureEngineer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models-dir", default="models", help="Directory with model artifacts")
    args = parser.parse_args()

    model_path = os.path.join(args.models_dir, "model.pkl")
    pipeline_path = os.path.join(args.models_dir, "feature_pipeline.pkl")

    for path in [model_path, pipeline_path]:
        if not os.path.exists(path):
            print(f"FAIL: {path} not found")
            return

    # Load artifacts
    model = joblib.load(model_path)
    fe = joblib.load(pipeline_path)

    # Verify types
    assert isinstance(fe, FeatureEngineer), f"feature_pipeline.pkl is {type(fe)}, expected FeatureEngineer"
    assert hasattr(model, "predict"), "model.pkl has no predict method"
    assert hasattr(model, "predict_proba"), "model.pkl has no predict_proba method"

    # Smoke test: transform a dummy row through the pipeline and predict
    dummy = pd.DataFrame([{
        "timestamp": "2026-01-01T00:00:00",
        "cpu": 50.0, "ram": 60.0, "latency": 0.03,
        "disk_io": 500.0, "network_io": 500.0, "deploy_flag": 0,
    }])
    transformed = fe.transform(dummy)
    prob = model.predict_proba(transformed)[:, 1]

    print(f"OK: feature_pipeline.pkl loaded ({type(fe).__name__}, window={fe.window_size})")
    print(f"OK: model.pkl loaded ({type(model).__name__})")
    print(f"OK: smoke test prediction probability = {prob[0]:.4f}")


if __name__ == "__main__":
    main()
