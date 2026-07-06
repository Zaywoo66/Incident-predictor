import os
import sys

import joblib
import shap

# Ensure ml-pipeline/features.py is importable (needed for FeatureEngineer deserialization)
_ML_PIPELINE_DIR = os.path.join(os.path.dirname(__file__), "..", "ml-pipeline")
if os.path.isdir(_ML_PIPELINE_DIR) and _ML_PIPELINE_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(_ML_PIPELINE_DIR))


def load_models(models_dir: str | None = None):
    """Load model, feature pipeline, and SHAP explainer from disk.

    Args:
        models_dir: Path to directory containing model.pkl and
            feature_pipeline.pkl. Falls back to MODELS_DIR env var,
            then to ../ml-pipeline/models.

    Returns:
        Tuple of (model, feature_pipeline, explainer).
    """
    if models_dir is None:
        models_dir = os.environ.get(
            "MODELS_DIR",
            os.path.join(os.path.dirname(__file__), "..", "ml-pipeline", "models"),
        )

    model_path = os.path.join(models_dir, "model.pkl")
    pipeline_path = os.path.join(models_dir, "feature_pipeline.pkl")

    model = joblib.load(model_path)
    feature_pipeline = joblib.load(pipeline_path)
    explainer = shap.TreeExplainer(model)

    return model, feature_pipeline, explainer
