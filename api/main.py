from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from model_loader import load_models
from schemas import HealthResponse, PredictRequest, PredictResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    model, feature_pipeline, explainer = load_models()
    app.state.model = model
    app.state.feature_pipeline = feature_pipeline
    app.state.explainer = explainer
    yield


app = FastAPI(title="Incident Predictor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для локальной разработки; сузить в проде
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    # Convert incoming points to DataFrame
    rows = [point.model_dump() for point in request.points]
    df = pd.DataFrame(rows)

    # Apply the same feature engineering used during training
    X = app.state.feature_pipeline.transform(df)

    # Predict probability for the last (most recent) data point
    probabilities = app.state.model.predict_proba(X)
    probability = float(probabilities[-1, 1])

    # Compute SHAP values for the last row
    last_row = X.iloc[[-1]]
    shap_vals = app.state.explainer.shap_values(last_row)

    # Handle both array shapes that TreeExplainer may return
    if isinstance(shap_vals, list):
        # Binary classification: shap_vals[1] = positive class
        vals = shap_vals[1][0] if len(shap_vals) > 1 else shap_vals[0][0]
    else:
        vals = shap_vals[0]

    shap_dict = {
        col: float(np.round(val, 6))
        for col, val in zip(last_row.columns, vals)
    }

    return PredictResponse(probability=probability, shap_values=shap_dict)
