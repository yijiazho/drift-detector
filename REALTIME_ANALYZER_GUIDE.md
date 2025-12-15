# Real-Time Drift Analyzer Guide

## Overview

The Real-Time Drift Analyzer monitors prediction log files in real-time and detects drift as predictions arrive, providing immediate alerts without waiting for batch processing.

## Architecture

```
Model Service → JSONL Log File → File Watcher (watchdog) → Real-Time Analyzer
                                        ↓
                                  Sliding Window Buffer
                                        ↓
                                  ADWIN Drift Detection
                                        ↓
                                  Console Alerts
```

## Key Features

- **Real-time monitoring**: Detects drift as predictions are logged (file tailing)
- **Zero infrastructure**: No message queues or databases required
- **Sliding window**: Maintains configurable window of recent predictions
- **ADWIN algorithm**: Uses River's ADWIN for adaptive drift detection
- **Graceful shutdown**: Ctrl+C shows final summary statistics
- **Auto-detection**: Can automatically find today's log file
- **Alert history**: Tracks all drift detection events
- **Periodic status**: Shows progress updates every 60 seconds

## Installation

Install the required dependency:

```bash
pip install watchdog==3.0.0
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Start the Model Service

```bash
# Terminal 1: Start model service
python src/model_service.py
```

### 2. Start Real-Time Analyzer

```bash
# Terminal 2: Start real-time drift analyzer
python realtime_drift_analyzer.py --auto
```

### 3. Run Drift Simulation

```bash
# Terminal 3: Run simulation to generate predictions
python src/drift_simulator.py --config configs/config_simple.json
```

You'll see drift alerts in Terminal 2 as they're detected in real-time!

## Usage

### Basic Usage

Monitor today's log file automatically:

```bash
python realtime_drift_analyzer.py --auto
```

Monitor a specific log file:

```bash
python realtime_drift_analyzer.py --log-file logs/predictions_20251214.jsonl
```

### Advanced Options

**Custom window size** (default: 100):
```bash
python realtime_drift_analyzer.py --auto --window-size 50
```

**Adjust sensitivity** (lower delta = more sensitive, default: 0.002):
```bash
# More sensitive (detect smaller changes)
python realtime_drift_analyzer.py --auto --delta 0.001

# Less sensitive (only detect larger changes)
python realtime_drift_analyzer.py --auto --delta 0.01
```

**Quiet mode** (only show drift alerts):
```bash
python realtime_drift_analyzer.py --auto --quiet
```

**Combined options**:
```bash
python realtime_drift_analyzer.py \
  --log-file logs/predictions_20251214.jsonl \
  --window-size 50 \
  --delta 0.001 \
  --quiet
```

## Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--log-file` | str | - | Path to prediction log file to monitor |
| `--auto` | flag | - | Auto-detect today's log file (logs/predictions_YYYYMMDD.jsonl) |
| `--window-size` | int | 100 | Number of predictions per analysis window |
| `--delta` | float | 0.002 | ADWIN sensitivity (0.001-0.01 recommended) |
| `--quiet` | flag | - | Only show drift alerts, suppress status updates |

## Output Format

### Drift Alert (when drift detected)

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

### Normal Window (no drift)

```
======================================================================
✓ Window 0 Complete
======================================================================
Timestamp:        2025-12-14T20:44:12.987654Z
Status:           STABLE
Drift Statistic:  0.000000
Baseline Mean:    0.071059
Current Mean:     0.071059
Current Std:      0.085500
Predictions:      100

✓ Stable - Mean: 0.0711, Baseline: 0.0711
======================================================================
```

### Status Update (every 60 seconds)

```
----------------------------------------------------------------------
📊 Status Update - 20:45:00
----------------------------------------------------------------------
Predictions processed: 250
Windows analyzed:      2
Drift detected:        1 (50.0%)
Current window:        50/100 predictions
----------------------------------------------------------------------
```

### Final Summary (on Ctrl+C)

```
🛑 Shutting down gracefully...

======================================================================
FINAL SUMMARY
======================================================================
Total predictions:     400
Total windows:         4
Drift detected:        2 windows
Detection rate:        50.0%
Baseline mean:         0.071059
======================================================================
```

## How It Works

### 1. File Monitoring

Uses `watchdog` library to monitor the logs directory for file modifications:
- Watches for changes to the specified JSONL file
- Maintains file position to only read new lines (tail behavior)
- Handles log file rotation gracefully

### 2. Sliding Window

Maintains a deque (double-ended queue) of predictions:
- Fixed maximum size (configurable via `--window-size`)
- Automatically discards oldest predictions when full
- Allows efficient O(1) additions and removals

### 3. Drift Detection

Uses ADWIN (Adaptive Windowing) algorithm:
- Processes each prediction value immediately
- Maintains adaptive window internally
- Detects change points in data distribution
- No assumptions about data distribution

### 4. Alert Generation

Creates alerts when windows complete:
- Calculates statistics (mean, std, drift statistic)
- Compares against baseline (first window)
- Generates human-readable messages
- Tracks alert history

## Integration with Existing Tools

### With Model Service

The analyzer works transparently with the existing model service:
- No changes needed to `src/model_service.py`
- Monitors the same JSONL logs
- Can run alongside batch `drift_detector.py`

### With Drift Simulator

Perfect for testing:
```bash
# Terminal 1: Model service
python src/model_service.py

# Terminal 2: Real-time analyzer
python realtime_drift_analyzer.py --auto

# Terminal 3: Simulation
python src/drift_simulator.py --config configs/config_simple.json
```

Watch drift detection happen in real-time!

### With Dashboard

Can run simultaneously:
- Real-time analyzer: Live alerts in terminal
- Dashboard: Visual analysis after the fact
- Both read the same log files

## Performance Characteristics

### Latency

- **File write to detection**: ~10-500ms (depends on OS file system)
- **Per-prediction overhead**: <1ms
- **Window analysis**: ~5-10ms

### Resource Usage

- **Memory**: ~1-10MB (depends on window size)
- **CPU**: <1% (idle), 5-10% (active simulation)
- **Disk I/O**: Minimal (only reads new lines)

### Scalability

Good for:
- ✅ 1-100 predictions/second
- ✅ Window sizes up to 10,000
- ✅ Long-running sessions (hours/days)

Not ideal for:
- ❌ >1000 predictions/second (use message queue)
- ❌ Distributed deployments (use Redis/Kafka)
- ❌ Multiple log files simultaneously

## Troubleshooting

### Log file not found

**Problem**: `Warning: Log file does not exist yet`

**Solution**: This is normal! The analyzer waits for the file to be created. Start the model service or run a simulation.

### No alerts appearing

**Possible causes**:
1. No predictions being logged (check model service is running)
2. Window not complete yet (need 100 predictions by default)
3. No drift in data (check with `analyze_drift.py`)
4. Delta too high (try `--delta 0.001`)

### Drift detected too frequently

**Solution**: Increase delta for less sensitivity:
```bash
python realtime_drift_analyzer.py --auto --delta 0.01
```

### Missing predictions

**Problem**: Predictions seem to be skipped

**Possible causes**:
1. File was modified while reading (rare race condition)
2. Invalid JSON in log file
3. Log file was rotated

**Solution**: The analyzer is resilient to these issues and will continue processing.

## Comparison: Real-time vs Batch

| Feature | Real-time Analyzer | Batch Detector |
|---------|-------------------|----------------|
| **Latency** | Seconds | Minutes to hours |
| **Use case** | Live monitoring | Post-hoc analysis |
| **Resource usage** | Minimal | Higher (loads all data) |
| **Flexibility** | Limited | Full historical analysis |
| **Output** | Console alerts | JSON files + reports |
| **Best for** | Production monitoring | Research & validation |

## Best Practices

### 1. Choose Appropriate Window Size

- **Small windows (50-100)**: Faster detection, more false positives
- **Large windows (200-500)**: Slower detection, more reliable
- **Default (100)**: Good balance for most use cases

### 2. Tune Delta Parameter

- **Sensitive (0.001)**: Detect subtle drift, may have false positives
- **Moderate (0.002)**: Default, good for most scenarios
- **Conservative (0.01)**: Only detect significant drift

### 3. Monitor Multiple Sessions

Use different terminals for different log files:
```bash
# Terminal 1: Production logs
python realtime_drift_analyzer.py --log-file logs/production.jsonl

# Terminal 2: Test logs
python realtime_drift_analyzer.py --log-file logs/test.jsonl
```

### 4. Integrate with Alerting

Use the alert callback for custom integrations:
```python
def send_slack_alert(alert: DriftAlert):
    if alert.drift_detected:
        # Send to Slack, email, etc.
        pass

analyzer = RealtimeDriftDetector(alert_callback=send_slack_alert)
```

## Future Enhancements

Potential improvements (not yet implemented):

1. **Multiple log files**: Monitor all files in logs/ directory
2. **Alert destinations**: Webhook, email, Slack integration
3. **Persistent state**: Save/restore detector state across restarts
4. **Metrics export**: Prometheus/StatsD metrics
5. **Web UI**: Real-time dashboard with WebSocket
6. **Configurable alerts**: Threshold-based alerting rules

## Examples

### Example 1: Quick Test

```bash
# Start model service
python src/model_service.py &

# Start real-time analyzer
python realtime_drift_analyzer.py --auto &

# Run simulation
python src/drift_simulator.py --config configs/config_simple.json

# You'll see:
# - Window 0 (baseline): STABLE
# - Window 1 (baseline): STABLE
# - Window 2 (drift): DRIFT DETECTED! 🚨
# - Window 3 (drift): DRIFT DETECTED! 🚨
```

### Example 2: Sensitive Detection

```bash
# Detect even small changes
python realtime_drift_analyzer.py --auto --delta 0.0001 --window-size 50
```

### Example 3: Quiet Monitoring

```bash
# Only see drift alerts, no status updates
python realtime_drift_analyzer.py --auto --quiet > drift_alerts.log 2>&1
```

## Architecture Details

### Class Hierarchy

```
RealtimeDriftAnalyzer (main orchestrator)
├── RealtimeDriftDetector (ADWIN + statistics)
│   ├── PredictionWindow (sliding window buffer)
│   └── ADWIN (River library)
└── PredictionLogMonitor (file watcher)
    └── FileSystemEventHandler (watchdog)
```

### Data Flow

```
1. Model Service writes prediction to JSONL
2. Watchdog detects file modification
3. PredictionLogMonitor reads new line
4. PredictionWindow adds to buffer
5. RealtimeDriftDetector processes with ADWIN
6. If window complete → analyze and alert
7. Print alert to console
8. Continue monitoring...
```

## API Reference

### RealtimeDriftAnalyzer

Main application class.

```python
analyzer = RealtimeDriftAnalyzer(
    log_file=Path("logs/predictions.jsonl"),
    window_size=100,
    delta=0.002,
    verbose=True
)
analyzer.start()  # Blocks until Ctrl+C
```

### RealtimeDriftDetector

Core drift detection logic.

```python
detector = RealtimeDriftDetector(
    window_size=100,
    delta=0.002,
    alert_callback=my_callback  # Optional
)

alert = detector.process_prediction(prediction_dict)
summary = detector.get_summary()
```

### DriftAlert

Alert data structure.

```python
@dataclass
class DriftAlert:
    window_id: int
    timestamp: str
    drift_detected: bool
    drift_statistic: float
    baseline_mean: float
    current_mean: float
    current_std: float
    predictions_in_window: int
    alert_message: str
```

## Contributing

To extend the real-time analyzer:

1. Add custom alert handlers in `RealtimeDriftDetector`
2. Implement new monitoring strategies in `PredictionLogMonitor`
3. Add metrics export in `RealtimeDriftAnalyzer`

## License

Same as main project (see LICENSE file).
