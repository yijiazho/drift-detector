# Drift Detection System

A comprehensive machine learning drift detection system with synthetic data generation, model serving, and real-time drift monitoring.

## Overview

This system implements a complete pipeline for detecting data drift in machine learning models:

- **Epic 1**: Local Model Service with prediction logging
- **Epic 2**: Synthetic data generation with configurable drift simulation
- **Epic 3**: ADWIN-based drift detection engine
- **Epic 4**: Visualization dashboard (Coming soon)

## Features

### ✅ Epic 1: Local Model Service

- FastAPI-based prediction service
- Pre-fitted scikit-learn Logistic Regression model
- Automatic prediction logging in JSONL format
- Health check endpoint
- Request/response validation with Pydantic

### ✅ Epic 2: Synthetic Stream & Drift Simulator

- Configurable synthetic data generation
- Multiple drift phases (baseline, gradual drift, abrupt drift)
- Windowing with metadata tracking
- Configurable request rates and window sizes
- Ground truth drift labels for validation

### ✅ Epic 3: Drift Detection Engine

- ADWIN (Adaptive Windowing) algorithm from River library
- Automatic drift detection on prediction streams
- Configurable sensitivity (delta parameter)
- Statistical drift metrics (mean difference from baseline)
- Ground truth comparison and accuracy metrics
- JSON output with detection results per window

## Quick Start

### 1. Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create the pre-fitted model
python create_model.py
```

### 2. Start the Model Service

```bash
# Terminal 1: Start the FastAPI service
source venv/bin/activate
python src/model_service.py
```

The service will be available at `http://localhost:8000`

### 3. Run Drift Simulation

```bash
# Terminal 2: Run the drift simulator
source venv/bin/activate
python src/drift_simulator.py --config configs/config_simple.json
```

### 4. Detect Drift

```bash
# Terminal 3: Run drift detection
source venv/bin/activate
python src/drift_detector.py
```

### 5. Analyze Results

```bash
# View drift statistics
python analyze_drift.py
```

## Project Structure

```
drift-detector/
├── src/
│   ├── model_service.py          # FastAPI prediction service
│   ├── drift_simulator.py        # Drift simulation engine
│   └── drift_detector.py         # ADWIN drift detection engine
├── configs/
│   ├── config_simple.json        # Simple drift scenario
│   └── config_multiple_drifts.json  # Complex multi-phase scenario
├── models/
│   ├── model_v1.0.pkl            # Pre-fitted model
│   └── model_metadata.pkl        # Model metadata
├── logs/
│   └── predictions_*.jsonl       # Prediction logs
├── outputs/
│   ├── metadata/
│   │   └── window_metadata.json  # Window metadata with drift labels
│   └── detection/
│       └── drift_detection.json  # Drift detection results
├── create_model.py               # Model creation script
├── test_service.py               # Epic 1 test suite
├── analyze_drift.py              # Drift analysis tool
├── TODO.md                       # Future enhancements
└── requirements.txt              # Python dependencies
```

## Usage Guide

### Testing the Model Service (Epic 1)

Run the comprehensive test suite:

```bash
source venv/bin/activate
python test_service.py
```

This tests:
- Health check endpoint
- Prediction endpoint
- Multiple predictions
- Prediction logging

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/

# Make a prediction
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

**Response:**
```json
{
  "prediction": 0.016,
  "model_version": "v1.0",
  "timestamp": "2025-12-07T00:28:48.938254Z"
}
```

### Configuring Drift Scenarios

Create or modify JSON configuration files:

```json
{
  "simulation": {
    "request_rate": 20,           // Requests per second
    "total_requests": 400,        // Total number of requests
    "window_size": 100            // Predictions per window
  },
  "drift_phases": [
    {
      "phase_id": 1,
      "name": "baseline",
      "num_requests": 200,
      "is_drift": false,
      "drift_type": "none",
      "distribution": {
        "feature1": {"mean": 5.0, "std": 1.0},
        "feature2": {"mean": 2.0, "std": 0.5},
        "feature3": {"mean": 1.3, "std": 0.3}
      }
    },
    {
      "phase_id": 2,
      "name": "abrupt_drift",
      "num_requests": 200,
      "is_drift": true,
      "drift_type": "abrupt",
      "distribution": {
        "feature1": {"mean": 8.0, "std": 1.5},
        "feature2": {"mean": 3.0, "std": 0.8},
        "feature3": {"mean": 2.2, "std": 0.5}
      }
    }
  ]
}
```

### Running Different Scenarios

```bash
# Simple scenario: baseline → abrupt drift
python src/drift_simulator.py --config configs/config_simple.json

# Complex scenario: baseline → gradual → abrupt drift
python src/drift_simulator.py --config configs/config_multiple_drifts.json

# Custom output and endpoint
python src/drift_simulator.py \
  --config configs/config_simple.json \
  --output outputs/metadata/my_run.json \
  --url http://localhost:8000/predict
```

### Detecting Drift (Epic 3)

After running a simulation, detect drift using ADWIN:

```bash
# Basic usage (uses today's log file automatically)
python src/drift_detector.py

# Specify log file and parameters
python src/drift_detector.py \
  --log-file logs/predictions_20251208.jsonl \
  --metadata outputs/metadata/window_metadata.json \
  --window-size 100 \
  --delta 0.002 \
  --output outputs/detection/drift_detection.json

# More sensitive detection (lower delta)
python src/drift_detector.py --delta 0.001

# Less sensitive detection (higher delta)
python src/drift_detector.py --delta 0.01
```

**Parameters:**
- `--log-file`: Path to predictions JSONL file (default: today's date)
- `--metadata`: Path to window metadata (default: outputs/metadata/window_metadata.json)
- `--window-size`: Predictions per window (default: 100)
- `--delta`: ADWIN sensitivity (default: 0.002)
  - Lower = more sensitive (more detections)
  - Higher = less sensitive (fewer false positives)
- `--output`: Output file for detection results (default: outputs/detection/drift_detection.json)
```

## Data Formats

### Prediction Log Format

Stored in `logs/predictions_YYYYMMDD.jsonl`:

```json
{
  "timestamp": "2025-12-07T22:39:51.932594Z",
  "input_features": {
    "feature1": 5.23,
    "feature2": 1.98,
    "feature3": 1.25
  },
  "prediction": 0.0788,
  "model_version": "v1.0",
  "drift_phase": 1
}
```

### Window Metadata Format

Stored in `outputs/metadata/window_metadata.json`:

```json
{
  "window_id": 0,
  "start_timestamp": "2025-12-07T22:39:51.932594Z",
  "end_timestamp": "2025-12-07T22:39:57.739748Z",
  "is_drift": false,
  "is_simulated": true,
  "number_of_predictions": 100
}
```

### Drift Detection Output Format

Stored in `outputs/detection/drift_detection.json`:

```json
{
  "window_id": 2,
  "timestamp": "2025-12-08T00:30:39.573019Z",
  "drift_statistic": 0.429292,
  "drift_detected": true,
  "adwin_detected": true,
  "baseline_mean": 0.071059,
  "current_mean": 0.50035,
  "current_std": 0.320717,
  "predictions_processed": 100,
  "ground_truth_drift": true
}
```

## Example Results

### Simulation Output

```
============================================================
Drift Simulator - Epic 2
============================================================
Configuration:
  Request rate: 20 req/s
  Total requests: 400
  Window size: 100
  Drift phases: 2

✓ Model service is running: v1.0

→ Starting Phase 1: baseline (drift=False)
  ✓ Window 0 completed: 100 predictions, drift=False
  ✓ Window 1 completed: 100 predictions, drift=False

→ Entering Phase 2: abrupt_drift (drift=True)
  ✓ Window 2 completed: 100 predictions, drift=True
  ✓ Window 3 completed: 100 predictions, drift=True

============================================================
Simulation Complete
============================================================
Total requests sent: 400/400
Success rate: 100.0%
Total windows: 4
```

### Drift Analysis

```
Window 0 (drift=False):
  Mean:  0.0788  ← Baseline
  Std:   0.0855

Window 1 (drift=False):
  Mean:  0.0771  ← Baseline
  Std:   0.0670

Window 2 (drift=True):
  Mean:  0.4932  ← Drift detected! (6.5x increase)
  Std:   0.2753

Window 3 (drift=True):
  Mean:  0.5390  ← Drift continues
  Std:   0.2973
```

The prediction mean shifts from **~0.078** to **~0.52**, demonstrating clear, detectable drift.

### Drift Detection Output

```
======================================================================
Drift Detection Engine - Epic 3
======================================================================
Configuration:
  Window size: 100
  ADWIN delta: 0.002
  Total predictions: 400

Processing windows...
  Window  0: STABLE | stat=0.0000 | mean=0.0711 | Ground truth: STABLE ✓
  Window  1: STABLE | stat=0.0112 | mean=0.0823 | Ground truth: STABLE ✓
  Window  2: DRIFT  | stat=0.4293 | mean=0.5003 | Ground truth: DRIFT ✓
  Window  3: STABLE | stat=0.4830 | mean=0.5541 | Ground truth: DRIFT ✗

======================================================================
Detection Summary
======================================================================
Total windows: 4
Drift detected: 1
Stable: 3

Ground Truth Comparison:
  Accuracy: 75.0% (3/4)
  True Positives:  1
  False Positives: 0
  True Negatives:  2
  False Negatives: 1
  Precision: 1.00
  Recall: 0.50
```

**Interpretation:**
- ADWIN detected drift in window 2 (first drift window) ✓
- Window 3 marked as stable because ADWIN already adapted to the new distribution
- This is expected behavior: ADWIN detects the *change*, not the ongoing *state*
- Perfect precision (no false positives)
- 50% recall (missed detecting continuation in window 3)

## Development

### Adding New Features

1. Model service endpoints: Edit `src/model_service.py`
2. Drift simulation logic: Edit `src/drift_simulator.py`
3. Configuration schemas: Create new JSON config files

### Running Tests

```bash
# Epic 1 tests
python test_service.py

# Drift analysis
python analyze_drift.py
```

### Viewing Logs

```bash
# Latest predictions
tail -f logs/predictions_*.jsonl

# Window metadata
cat outputs/metadata/window_metadata.json | python -m json.tool

# Drift detection results
cat outputs/detection/drift_detection.json | python -m json.tool
```

## Dependencies

- `fastapi==0.104.1` - Web framework
- `uvicorn==0.24.0` - ASGI server
- `scikit-learn==1.3.2` - ML model
- `numpy==1.26.2` - Numerical computing
- `pydantic==2.5.0` - Data validation
- `river==0.21.0` - Streaming ML algorithms (ADWIN)
- `requests` - HTTP client (for testing)

## API Reference

### Health Check

**GET** `/`

Returns service status and model version.

### Predict

**POST** `/predict`

**Request:**
```json
{
  "features": {
    "feature1": 3.5,
    "feature2": 1.2,
    "feature3": 0.8
  }
}
```

**Response:**
```json
{
  "prediction": 0.5,
  "model_version": "v1.0",
  "timestamp": "2025-11-21T10:00:00Z"
}
```

## Roadmap

- [x] Epic 1: Local Model Service
- [x] Epic 2: Synthetic Stream & Drift Simulator
- [x] Epic 3: Drift Detection Engine (ADWIN)
- [ ] Epic 4: Visualization Dashboard
- [ ] Epic 5: Storage & Integration

See [TODO.md](TODO.md) for planned enhancements and future features.

## License

See LICENSE file for details.
