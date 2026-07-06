from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from httpx import ASGITransport, AsyncClient

# Number of features produced by FeatureEngineer for 5 metric columns:
# Each column gets 4 derived features (mean, std, lag1, roc) = 20
# Plus original 6 columns (cpu, ram, latency, disk_io, network_io, deploy_flag) = 26
_NUM_FEATURES = 26


def _make_mock_models():
    """Create mock model, feature_pipeline, and explainer."""
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])

    mock_pipeline = MagicMock()
    # transform returns a DataFrame-like object with .iloc and .columns
    import pandas as pd

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
    with patch("model_loader.load_models") as mock_load:
        mock_load.return_value = (mock_model, mock_pipeline, mock_explainer)
        # Import app after patching so lifespan uses the mock
        from main import app

        yield app


@pytest.mark.anyio
async def test_health(mock_models):
    transport = ASGITransport(app=mock_models)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
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


@pytest.mark.anyio
async def test_predict_empty_points(mock_models):
    transport = ASGITransport(app=mock_models)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/predict",
            json={"points": [], "window_minutes": 5},
        )
    assert response.status_code == 422
