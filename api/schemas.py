from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    timestamp: str
    cpu: float
    ram: float
    latency: float
    disk_io: float
    network_io: float
    deploy_flag: int


class PredictRequest(BaseModel):
    points: list[MetricPoint] = Field(..., min_length=1)
    window_minutes: int = Field(default=5, gt=0)


class PredictResponse(BaseModel):
    probability: float
    shap_values: dict[str, float]


class HealthResponse(BaseModel):
    status: str
