import sys
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

_NUM_FEATURES = 26


def _make_mock_models():
    """Create mock model, feature_pipeline, and explainer."""
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])

    mock_pipeline = MagicMock()
    fake_features = pd.DataFrame(
        np.random.rand(1, _NUM_FEATURES),
        columns=[f"feat_{i}" for i in range(_NUM_FEATURES)],
    )
    mock_pipeline.transform.return_value = fake_features

    mock_explainer = MagicMock()
    mock_explainer.shap_values.return_value = [
        np.random.rand(1, _NUM_FEATURES),
        np.random.rand(1, _NUM_FEATURES),
    ]

    return mock_model, mock_pipeline, mock_explainer


def _make_points(n: int = 10) -> list[dict]:
    return [
        {
            "timestamp": f"2026-01-01T00:{i:02d}:00",
            "cpu": 50.0 + i,
            "ram": 60.0,
            "latency": 0.03,
            "disk_io": 500.0,
            "network_io": 500.0,
            "deploy_flag": 0,
        }
        for i in range(n)
    ]


@pytest.fixture()
def mock_models():
    mock_model, mock_pipeline, mock_explainer = _make_mock_models()

    # Mock heavy modules that model_loader imports at the top level
    # so tests run without the full ML stack installed
    mock_shap = MagicMock()
    mock_joblib = MagicMock()
    original_modules = {}
    for mod_name in ("shap", "joblib"):
        original_modules[mod_name] = sys.modules.get(mod_name)
        sys.modules[mod_name] = mock_shap if mod_name == "shap" else mock_joblib

    # Clear cached imports so model_loader and main reload with mocks
    for mod_name in ("model_loader", "main"):
        sys.modules.pop(mod_name, None)

    import model_loader

    model_loader.load_models = MagicMock(
        return_value=(mock_model, mock_pipeline, mock_explainer)
    )

    sys.modules.pop("main", None)
    from main import app

    # ASGITransport doesn't trigger lifespan, so populate state manually
    app.state.model = mock_model
    app.state.feature_pipeline = mock_pipeline
    app.state.explainer = mock_explainer

    yield app

    # Restore original modules
    for mod_name, original in original_modules.items():
        if original is None:
            sys.modules.pop(mod_name, None)
        else:
            sys.modules[mod_name] = original
    for mod_name in ("model_loader", "main"):
        sys.modules.pop(mod_name, None)


@pytest.mark.asyncio
async def test_health(mock_models):
    transport = ASGITransport(app=mock_models)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_predict_valid(mock_models):
    transport = ASGITransport(app=mock_models)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/predict",
            json={"points": _make_points(10), "window_minutes": 5},
        )
    assert response.status_code == 200
    data = response.json()
    assert "probability" in data
    assert "shap_values" in data
    assert isinstance(data["probability"], float)
    assert isinstance(data["shap_values"], dict)


@pytest.mark.asyncio
async def test_predict_empty_points(mock_models):
    transport = ASGITransport(app=mock_models)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/predict",
            json={"points": [], "window_minutes": 5},
        )
    assert response.status_code == 422
