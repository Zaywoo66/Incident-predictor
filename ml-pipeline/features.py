import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Generates rolling time-series features (mean, std, lag, rate of change)
    from raw infrastructure metrics. Designed to be serialized and reused
    in both training and inference (api/) pipelines.
    """
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.feature_cols = ["cpu", "ram", "latency", "disk_io", "network_io"]

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()
        
        # Sort by timestamp if it exists to ensure correct rolling calculations
        if "timestamp" in df.columns:
            df = df.sort_values(by="timestamp").reset_index(drop=True)
            
        for col in self.feature_cols:
            if col not in df.columns:
                continue
                
            # Rolling statistics
            df[f"{col}_mean"] = df[col].rolling(window=self.window_size, min_periods=1).mean()
            df[f"{col}_std"] = df[col].rolling(window=self.window_size, min_periods=1).std().fillna(0)
            
            # Lag feature
            df[f"{col}_lag1"] = df[col].shift(1).fillna(df[col])
            
            # Rate of change (percentage change)
            # Add epsilon to prevent division by zero
            shifted = df[col].shift(1).fillna(df[col])
            roc = (df[col] - shifted) / (shifted + 1e-9)
            df[f"{col}_roc"] = roc.replace([np.inf, -np.inf], 0).fillna(0)
            
        # Drop timestamp as it shouldn't be used for model training directly
        if "timestamp" in df.columns:
            df = df.drop(columns=["timestamp"])
            
        return df
