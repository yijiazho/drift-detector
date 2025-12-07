"""
FastAPI Model Service for Drift Detection System.
Implements Epic 1: Local Model Service with prediction endpoint and logging.
"""
import pickle
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Request and Response Models
class PredictionRequest(BaseModel):
    features: Dict[str, float]


class PredictionResponse(BaseModel):
    prediction: float
    model_version: str
    timestamp: str


# Initialize FastAPI app
app = FastAPI(title="Drift Detection Model Service")

# Global variables for model and metadata
model = None
metadata = None
logs_dir = Path("logs")


@app.on_event("startup")
async def load_model():
    """Load the pre-trained model and metadata at startup."""
    global model, metadata

    model_path = "models/model_v1.0.pkl"
    metadata_path = "models/model_metadata.pkl"

    try:
        # Load model
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        print(f"✓ Model loaded successfully from {model_path}")

        # Load metadata
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
        print(f"✓ Metadata loaded successfully from {metadata_path}")
        print(f"  Model version: {metadata['version']}")
        print(f"  Model type: {metadata['model_type']}")
        print(f"  Features: {metadata['feature_names']}")

        # Ensure logs directory exists
        logs_dir.mkdir(exist_ok=True)
        print(f"✓ Logs directory ready at {logs_dir}")

    except FileNotFoundError as e:
        print(f"✗ Error loading model: {e}")
        print("  Please run create_model.py first to generate the model files.")
        raise


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "model_version": metadata["version"] if metadata else "unknown",
        "service": "Drift Detection Model Service"
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make predictions on input features.

    Args:
        request: PredictionRequest containing features dict

    Returns:
        PredictionResponse with prediction, model version, and timestamp
    """
    if model is None or metadata is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Extract features in correct order
        feature_names = metadata["feature_names"]
        features_array = np.array([[
            request.features.get(name, 0.0) for name in feature_names
        ]])

        # Make prediction (probability of positive class)
        prediction = float(model.predict_proba(features_array)[0][1])

        # Create timestamp
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Log the prediction (Epic 1, Task 1.2)
        log_prediction(
            timestamp=timestamp,
            input_features=request.features,
            prediction=prediction,
            model_version=metadata["version"]
        )

        # Return response
        return PredictionResponse(
            prediction=prediction,
            model_version=metadata["version"],
            timestamp=timestamp
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


def log_prediction(
    timestamp: str,
    input_features: Dict[str, float],
    prediction: float,
    model_version: str,
    drift_phase: int = 1
):
    """
    Log prediction to JSON file.

    Args:
        timestamp: ISO format timestamp
        input_features: Dictionary of input features
        prediction: Model prediction value
        model_version: Version of the model used
        drift_phase: Current drift phase (default: 1)
    """
    log_entry = {
        "timestamp": timestamp,
        "input_features": input_features,
        "prediction": prediction,
        "model_version": model_version,
        "drift_phase": drift_phase
    }

    # Create log filename based on date
    date_str = datetime.utcnow().strftime("%Y%m%d")
    log_file = logs_dir / f"predictions_{date_str}.jsonl"

    # Append to JSONL file (one JSON object per line)
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
