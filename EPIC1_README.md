# Epic 1: Local Model Service

This implementation provides a FastAPI-based model service with prediction endpoint and automatic logging.

## Features

✅ **Task 1.1: FastAPI Model Service**
- Pre-fitted scikit-learn Logistic Regression model
- `/predict` endpoint for making predictions
- Model loaded at startup
- Request/response schemas match specification

✅ **Task 1.2: Prediction Logging**
- Automatic logging of all predictions
- Structured JSON format (JSONL)
- Logs stored in `logs/` directory
- Includes timestamp, features, prediction, model version, and drift phase

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create the Model

```bash
python create_model.py
```

This creates:
- `models/model_v1.0.pkl` - Pre-fitted logistic regression model
- `models/model_metadata.pkl` - Model metadata

## Running the Service

### Start the FastAPI Server

```bash
python src/model_service.py
```

Or with uvicorn directly:

```bash
uvicorn src.model_service:app --reload
```

The service will start on `http://localhost:8000`

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/
```

### Make Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "feature1": 3.5,
      "feature2": 1.2,
      "feature3": 0.8
    }
  }'
```

**Expected Response:**
```json
{
  "prediction": 0.5,
  "model_version": "v1.0",
  "timestamp": "2025-11-21T10:00:00Z"
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_service.py
```

This will test:
- Health check endpoint
- Prediction endpoint
- Multiple predictions
- Prediction logging

## Log Format

Predictions are logged to `logs/predictions_YYYYMMDD.jsonl` in the following format:

```json
{
  "timestamp": "2025-11-21T10:00:00Z",
  "input_features": {
    "feature1": 3.5,
    "feature2": 1.2,
    "feature3": 0.8
  },
  "prediction": 0.5,
  "model_version": "v1.0",
  "drift_phase": 1
}
```

## Project Structure

```
drift-detector/
├── src/
│   └── model_service.py      # FastAPI service
├── models/
│   ├── model_v1.0.pkl        # Trained model
│   └── model_metadata.pkl    # Model metadata
├── logs/
│   └── predictions_*.jsonl   # Prediction logs
├── create_model.py           # Model creation script
├── test_service.py           # Test suite
└── requirements.txt          # Python dependencies
```

## Acceptance Criteria

✅ FastAPI app runs locally
✅ Model loads successfully at startup
✅ `/predict` endpoint is reachable via HTTP
✅ Request and response match defined schemas
✅ Logs match schema exactly
✅ Logs persist to local JSON files
✅ Drift phase is properly recorded
