# api

Prediction service exposing XGBoost model via FastAPI.

```bash
pip install -r requirements.txt
MODELS_DIR=../ml-pipeline/models uvicorn main:app --reload
```

Env vars: `MODELS_DIR` — path to directory with `model.pkl` and `feature_pipeline.pkl` (default: `../ml-pipeline/models`).
