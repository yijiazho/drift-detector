# Guide: Drift Simulation

## Overview

This guide covers running drift simulations to generate synthetic data with configurable drift patterns for testing the drift detection system.

## Prerequisites

- ✅ Model service running (`python src/model_service.py`)
- ✅ Service accessible at http://localhost:8000
- ✅ Configuration file exists

## Quick Start

```bash
python src/drift_simulator.py --config configs/config_simple.json
```

## Available Configurations

### 1. Simple Configuration (Recommended for testing)

**File**: `configs/config_simple.json`

**Scenario**: Baseline → Abrupt Drift

```bash
python src/drift_simulator.py --config configs/config_simple.json
```

**What it does:**
- Sends 400 total requests
- 200 baseline predictions (no drift)
- 200 drifted predictions (abrupt drift)
- 4 windows of 100 predictions each
- 20 requests per second

### 2. Multiple Drifts Configuration

**File**: `configs/config_multiple_drifts.json`

**Scenario**: Baseline → Gradual Drift → Abrupt Drift

```bash
python src/drift_simulator.py --config configs/config_multiple_drifts.json
```

## Expected Output

```
============================================================
Drift Simulator - Epic 2
============================================================
Configuration:
  Request rate: 20 req/s
  Total requests: 400
  Window size: 100
  Drift phases: 2
  Predict endpoint: http://localhost:8000/predict

✓ Model service is running: v1.0

Starting simulation...

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
Failed requests: 0
Success rate: 100.0%
Elapsed time: 20.45s
Actual rate: 19.56 req/s
Total windows: 4

✓ Window metadata saved to outputs/metadata/window_metadata.json
  Total windows: 4
```

## Output Files

The simulator creates two types of outputs:

### 1. Prediction Logs

**Location**: `logs/predictions_YYYYMMDD.jsonl`

**Format**: One JSON object per line

```json
{
  "timestamp": "2025-12-14T20:45:32.123456Z",
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

### 2. Window Metadata

**Location**: `outputs/metadata/window_metadata.json`

**Format**: Array of window objects

```json
[
  {
    "window_id": 0,
    "start_timestamp": "2025-12-14T20:45:32.123456Z",
    "end_timestamp": "2025-12-14T20:45:37.234567Z",
    "is_drift": false,
    "is_simulated": true,
    "number_of_predictions": 100
  },
  {
    "window_id": 2,
    "start_timestamp": "2025-12-14T20:45:47.345678Z",
    "end_timestamp": "2025-12-14T20:45:52.456789Z",
    "is_drift": true,
    "is_simulated": true,
    "number_of_predictions": 100
  }
]
```

## Configuration File Format

### Basic Structure

```json
{
  "simulation": {
    "request_rate": 20,
    "total_requests": 400,
    "window_size": 100
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

### Simulation Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `request_rate` | int | Requests per second | 20 |
| `total_requests` | int | Total predictions to generate | 400 |
| `window_size` | int | Predictions per window | 100 |

### Phase Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `phase_id` | int | Unique phase identifier | 1 |
| `name` | string | Descriptive phase name | "baseline" |
| `num_requests` | int | Predictions in this phase | 200 |
| `is_drift` | bool | Is this a drift phase? | false |
| `drift_type` | string | Type of drift | "none", "gradual", "abrupt" |
| `distribution` | object | Feature distributions | See below |

### Feature Distribution

Each feature has a normal distribution:

```json
{
  "feature1": {
    "mean": 5.0,    // Mean value
    "std": 1.0      // Standard deviation
  }
}
```

## Command-Line Options

```bash
python src/drift_simulator.py [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--config` | config_simple.json | Path to configuration file |
| `--url` | http://localhost:8000/predict | Prediction endpoint URL |
| `--output` | outputs/metadata/window_metadata.json | Output file for metadata |

### Examples

**Custom configuration:**
```bash
python src/drift_simulator.py --config my_config.json
```

**Different endpoint:**
```bash
python src/drift_simulator.py --config configs/config_simple.json --url http://localhost:9000/predict
```

**Custom output location:**
```bash
python src/drift_simulator.py --config configs/config_simple.json --output outputs/my_simulation.json
```

## Creating Custom Scenarios

### Example 1: Quick Test (Fast)

```json
{
  "simulation": {
    "request_rate": 50,
    "total_requests": 100,
    "window_size": 25
  },
  "drift_phases": [
    {
      "phase_id": 1,
      "name": "baseline",
      "num_requests": 50,
      "is_drift": false,
      "drift_type": "none",
      "distribution": {
        "feature1": {"mean": 5.0, "std": 0.5},
        "feature2": {"mean": 2.0, "std": 0.3},
        "feature3": {"mean": 1.0, "std": 0.2}
      }
    },
    {
      "phase_id": 2,
      "name": "drift",
      "num_requests": 50,
      "is_drift": true,
      "drift_type": "abrupt",
      "distribution": {
        "feature1": {"mean": 8.0, "std": 0.5},
        "feature2": {"mean": 3.5, "std": 0.3},
        "feature3": {"mean": 2.0, "std": 0.2}
      }
    }
  ]
}
```

**Characteristics:**
- Completes in 2 seconds
- 4 windows total
- Clear drift signal

### Example 2: Subtle Drift

```json
{
  "drift_phases": [
    {
      "phase_id": 1,
      "name": "baseline",
      "distribution": {
        "feature1": {"mean": 5.0, "std": 1.0},
        "feature2": {"mean": 2.0, "std": 0.5},
        "feature3": {"mean": 1.5, "std": 0.3}
      }
    },
    {
      "phase_id": 2,
      "name": "subtle_drift",
      "is_drift": true,
      "drift_type": "gradual",
      "distribution": {
        "feature1": {"mean": 5.5, "std": 1.0},  // Small change
        "feature2": {"mean": 2.2, "std": 0.5},  // Small change
        "feature3": {"mean": 1.6, "std": 0.3}   // Small change
      }
    }
  ]
}
```

**Characteristics:**
- Hard to detect (small differences)
- Tests detection sensitivity
- Requires tuned ADWIN delta

## Monitoring the Simulation

### In Real-Time

While simulation runs, monitor in separate terminals:

**Terminal 1**: Model Service
```bash
python src/model_service.py
```

**Terminal 2**: Real-Time Analyzer
```bash
python realtime_drift_analyzer.py --auto --window-size 100
```

**Terminal 3**: Drift Simulation
```bash
python src/drift_simulator.py --config configs/config_simple.json
```

**Terminal 4**: Log Monitoring
```bash
tail -f logs/predictions_$(date +%Y%m%d).jsonl | jq -r '.prediction'
```

## Analyzing Results

After simulation completes:

### View Prediction Statistics

```bash
python analyze_drift.py --log-file logs/predictions_$(date +%Y%m%d).jsonl
```

### Run Drift Detection

```bash
python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl
```

### Visualize in Dashboard

```bash
streamlit run dashboard.py
```

## Troubleshooting

### Error: "Model service is not running"

**Solution**: Start the model service first
```bash
python src/model_service.py
```

### Error: "Configuration file not found"

**Solution**: Check file path
```bash
ls -l configs/
python src/drift_simulator.py --config configs/config_simple.json
```

### Low Success Rate

**Problem**: Not all requests succeed

**Possible Causes:**
1. Model service overloaded (reduce request_rate)
2. Network issues
3. Service restarting

**Solution**: Reduce request rate or increase timeout

### Predictions Look the Same

**Problem**: No visible drift in results

**Possible Causes:**
1. Feature distributions are too similar
2. Model is insensitive to the changes

**Solution**: Increase difference between distributions

## Performance Tips

### Fast Testing

```json
{
  "simulation": {
    "request_rate": 100,  // High rate
    "total_requests": 200,  // Few requests
    "window_size": 50  // Small windows
  }
}
```

### Realistic Scenario

```json
{
  "simulation": {
    "request_rate": 10,  // Moderate rate
    "total_requests": 1000,  // Many requests
    "window_size": 100  // Standard windows
  }
}
```

### Stress Test

```json
{
  "simulation": {
    "request_rate": 50,  // High rate
    "total_requests": 5000,  // Many requests
    "window_size": 100
  }
}
```

## Next Steps

After running simulation:

1. ✅ Simulation complete → Analyze results
   - See [Batch Detection Guide](05_batch_detection.md)
   - See [Real-Time Detection Guide](06_realtime_detection.md)

2. ✅ Drift detected → Visualize
   - See [Dashboard Guide](07_dashboard.md)

3. ✅ Results validated → Run own scenarios
   - Create custom configuration files
   - Test different drift patterns

## Related Guides

- [Model Service Guide](02_model_service.md)
- [Making Predictions](03_predictions.md)
- [Batch Drift Detection](05_batch_detection.md)
- [Real-Time Drift Detection](06_realtime_detection.md)
- [Dashboard Guide](07_dashboard.md)

## Additional Resources

- **src/drift_simulator.py**: Simulator source code
- **configs/**: Example configuration files
- **README.md**: Project overview
