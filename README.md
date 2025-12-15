# Drift Detection System

A comprehensive machine learning drift detection system with synthetic data generation, model serving, and real-time drift monitoring.

## Overview

This system implements a complete pipeline for detecting data drift in machine learning models:

- **Epic 1**: Local Model Service with prediction logging
- **Epic 2**: Synthetic data generation with configurable drift simulation
- **Epic 3**: ADWIN-based drift detection engine
- **Epic 4**: Streamlit visualization dashboard
- **Epic 5**: Unified storage schemas and integration tests

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

### ✅ Epic 4: Visualization Dashboard

- Interactive Streamlit web application
- Feature distribution visualization over time
- Drift detection results with ground truth comparison
- Time range filtering with window-based navigation
- Responsive charts using Plotly
- Log file selection and data exploration

### ✅ Epic 5: Storage & Integration

- Unified JSON Schema definitions for all data formats
- Schema validation with detailed error messages
- Data manager with type-safe operations
- Comprehensive end-to-end integration tests
- Automatic validation of existing data files
- Version-aware schema registry

### ✅ Real-Time Drift Analyzer

- Live drift detection using file tailing (no batch processing)
- Monitors prediction logs in real-time
- Immediate alerts when drift is detected
- Configurable sliding window and sensitivity
- Zero infrastructure requirements (no message queues)
- Graceful shutdown with summary statistics

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
python analyze_drift.py --log-file logs/predictions_YYYYMMDD.jsonl
```

### 6. Real-Time Drift Monitoring (NEW!)

```bash
# Terminal 4: Start real-time drift analyzer
python realtime_drift_analyzer.py --auto
```

This monitors predictions in real-time and alerts immediately when drift is detected!

### 7. Launch Dashboard

```bash
# Start the interactive dashboard
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### 8. Validate Data (Epic 5)

```bash
# Quick validation - verify all data and run tests
python validate_epic5.py

# Or run individually:
python src/data_manager.py           # Validate existing data files
python tests/test_integration.py     # Run integration tests
```

## Project Structure

```
drift-detector/
├── src/
│   ├── model_service.py          # FastAPI prediction service
│   ├── drift_simulator.py        # Drift simulation engine
│   ├── drift_detector.py         # ADWIN drift detection engine
│   └── data_manager.py           # Unified data operations (Epic 5)
├── schemas/                       # JSON Schema definitions (Epic 5)
│   ├── prediction_v1.json        # Prediction schema
│   ├── window_metadata_v1.json   # Window metadata schema
│   ├── drift_detection_v1.json   # Drift detection schema
│   ├── config_v1.json            # Configuration schema
│   └── schema_registry.py        # Schema validation utilities
├── tests/                         # Integration tests (Epic 5)
│   ├── __init__.py
│   └── test_integration.py       # End-to-end test suite
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
├── dashboard.py                  # Streamlit visualization dashboard
├── create_model.py               # Model creation script
├── analyze_drift.py              # Drift analysis tool (batch)
├── realtime_drift_analyzer.py    # Real-time drift monitor (NEW!)
├── test_realtime.py              # Real-time analyzer test script
├── guides/                       # User guides for all use cases
│   ├── README.md                # Guide index and navigation
│   ├── 01_creating_model.md
│   ├── 02_model_service.md
│   ├── 03_predictions.md
│   ├── 04_drift_simulation.md
│   ├── 05_batch_detection.md
│   ├── 06_realtime_detection.md
│   └── 07_dashboard.md
├── EPIC5_IMPLEMENTATION.md       # Epic 5 documentation
├── REALTIME_ANALYZER_GUIDE.md    # Real-time analyzer comprehensive guide
├── TODO.md                       # Future enhancements
└── requirements.txt              # Python dependencies
```

## User Guides

For detailed step-by-step instructions, see the **[guides/](guides/)** directory:

- **[Creating the Model](guides/01_creating_model.md)** - Generate the pre-fitted model
- **[Model Service](guides/02_model_service.md)** - Start and configure the FastAPI service
- **[Making Predictions](guides/03_predictions.md)** - Send predictions to the model
- **[Drift Simulation](guides/04_drift_simulation.md)** - Generate synthetic drift data
- **[Batch Detection](guides/05_batch_detection.md)** - Analyze logs for drift offline
- **[Real-Time Detection](guides/06_realtime_detection.md)** - Monitor drift in real-time
- **[Visualization Dashboard](guides/07_dashboard.md)** - Explore results interactively

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

### Real-Time Drift Monitoring (NEW!)

Monitor prediction logs in real-time and get immediate alerts when drift is detected:

```bash
# Auto-detect today's log file
python realtime_drift_analyzer.py --auto

# Monitor specific log file
python realtime_drift_analyzer.py --log-file logs/predictions_20251214.jsonl

# Custom window size and sensitivity
python realtime_drift_analyzer.py --auto --window-size 50 --delta 0.001

# Quiet mode (only show drift alerts)
python realtime_drift_analyzer.py --auto --quiet
```

**How it works:**
- Monitors JSONL log file using file tailing (like `tail -f`)
- Processes predictions as they arrive in real-time
- Maintains sliding window in memory
- Triggers ADWIN detection when window completes
- Prints alerts immediately to console
- Press Ctrl+C to see final summary

**Parameters:**
- `--auto`: Auto-detect today's log file (logs/predictions_YYYYMMDD.jsonl)
- `--log-file`: Path to specific prediction log file
- `--window-size`: Predictions per window (default: 100)
- `--delta`: ADWIN sensitivity (default: 0.002)
- `--quiet`: Only show drift alerts (no status updates)

**Example Output:**
```
======================================================================
🚨 DRIFT ALERT - Window 2
======================================================================
Timestamp:        2025-12-14T20:45:32.123456Z
Status:           DRIFT DETECTED
Drift Statistic:  0.429292
Baseline Mean:    0.071059
Current Mean:     0.500350
Current Std:      0.320717
Predictions:      100

🚨 DRIFT DETECTED! Mean shifted from 0.0711 to 0.5004 (+604.2%)
======================================================================
```

See [REALTIME_ANALYZER_GUIDE.md](REALTIME_ANALYZER_GUIDE.md) for detailed documentation.

### Visualization Dashboard (Epic 4)

Launch the interactive dashboard to visualize drift detection results:

```bash
streamlit run dashboard.py
```

**Dashboard Features:**
- **Feature Selection**: Choose which feature to visualize from dropdown
- **Time Series Plot**: View feature values over time with drift markers
- **Distribution Histogram**: See feature value distribution
- **Drift Detection Chart**: Visualize drift statistics with detection points
- **Ground Truth Comparison**: Compare detected drift vs actual drift (if available)
- **Time Range Filtering**: Use slider to filter by window range
- **Log File Selection**: Switch between different prediction log files

**Tips:**
- The dashboard automatically loads the latest log file
- Use the window range slider to zoom into specific time periods
- Hover over charts for detailed information
- Red vertical lines indicate detected drift points
- Green/red markers show true/false positives in detection

### Schema Validation & Integration Tests (Epic 5)

Validate data integrity and run end-to-end tests:

```bash
# Validate all existing data files
python src/data_manager.py

# Run comprehensive integration tests
python tests/test_integration.py
```

**Validation Output:**
```
✓ predictions_20251210.jsonl
✓ window_metadata.json
✓ drift_detection.json
✓ config_simple.json
Summary: 6/6 files passed validation
```

**Integration Tests:**
- Configuration validation
- Model service health check
- Prediction log validation
- Window metadata validation
- Drift detection validation
- Data consistency checks
- Ground truth comparison
- Schema error handling

**Using the Data Manager in Code:**
```python
from src.data_manager import DataManager
from pathlib import Path

# Initialize with validation
dm = DataManager(validate=True)

# Read data with automatic validation
config = dm.read_config(Path('configs/config_simple.json'))
predictions = dm.read_predictions(Path('logs/predictions_20251210.jsonl'))
windows = dm.read_window_metadata(Path('outputs/metadata/window_metadata.json'))
detections = dm.read_drift_detections(Path('outputs/detection/drift_detection.json'))

# Write data with validation
dm.write_window_metadata(output_file, windows_list)
dm.write_drift_detections(output_file, detections_list)
```

For detailed Epic 5 documentation, see [EPIC5_IMPLEMENTATION.md](EPIC5_IMPLEMENTATION.md)

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

### Testing

**Comprehensive Test Plan**: 143+ test cases across all epics documented in `TEST_PLAN.md`

**Current Tests**:
```bash
# Epic 1: Model Service Tests
python test_service.py

# Epic 5: Integration Tests
python tests/test_integration.py

# Run all tests with pytest
pytest tests/ -v

# With coverage report
pytest --cov=src --cov-report=html
```

**Test Coverage**:
- ✅ Epic 1: Basic model service tests (4 tests)
- ✅ Epic 5: Integration tests (11 tests)
- ○ Full test suite: 143+ tests documented, ready to implement

**Install Test Dependencies**:
```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio httpx
```

See [TEST_PLAN.md](TEST_PLAN.md) for complete test specifications and [TEST_PLAN_SUMMARY.md](TEST_PLAN_SUMMARY.md) for implementation guide.

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
- `streamlit==1.29.0` - Dashboard framework
- `plotly==5.18.0` - Interactive visualizations
- `jsonschema==4.20.0` - JSON Schema validation (Epic 5)
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
- [x] Epic 4: Visualization Dashboard
- [x] Epic 5: Storage & Integration

See [TODO.md](TODO.md) for planned enhancements and future features.

## License

See LICENSE file for details.
