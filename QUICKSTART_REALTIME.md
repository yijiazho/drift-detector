# Real-Time Drift Analyzer - Quick Start

## Installation

```bash
pip install watchdog==3.0.0
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Basic Usage

### Start Everything

```bash
# Terminal 1: Model Service
python src/model_service.py

# Terminal 2: Real-Time Analyzer
python realtime_drift_analyzer.py --auto

# Terminal 3: Drift Simulation
python src/drift_simulator.py --config configs/config_simple.json
```

Watch Terminal 2 for real-time drift alerts!

## Common Commands

### Auto-detect Today's Log
```bash
python realtime_drift_analyzer.py --auto
```

### Monitor Specific File
```bash
python realtime_drift_analyzer.py --log-file logs/predictions_20251214.jsonl
```

### Smaller Window (Faster Detection)
```bash
python realtime_drift_analyzer.py --auto --window-size 50
```

### More Sensitive Detection
```bash
python realtime_drift_analyzer.py --auto --delta 0.001
```

### Quiet Mode (Only Drift Alerts)
```bash
python realtime_drift_analyzer.py --auto --quiet
```

## What You'll See

### When Drift is Detected

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

### Normal Window (No Drift)

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

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--auto` | - | Auto-detect today's log file |
| `--log-file` | - | Specific log file path |
| `--window-size` | 100 | Predictions per window |
| `--delta` | 0.002 | ADWIN sensitivity (0.001-0.01) |
| `--quiet` | False | Only show drift alerts |

## Tips

### Tuning Sensitivity

**More Sensitive** (detect smaller changes):
```bash
python realtime_drift_analyzer.py --auto --delta 0.001
```

**Less Sensitive** (only detect significant drift):
```bash
python realtime_drift_analyzer.py --auto --delta 0.01
```

### Tuning Window Size

**Smaller Windows** (faster detection, more false positives):
```bash
python realtime_drift_analyzer.py --auto --window-size 50
```

**Larger Windows** (slower detection, more reliable):
```bash
python realtime_drift_analyzer.py --auto --window-size 200
```

## Testing

Quick test with the test script:

```bash
# Terminal 1: Start analyzer
python realtime_drift_analyzer.py --log-file logs/test_realtime.jsonl --window-size 10

# Terminal 2: Run test
python test_realtime.py
```

## Stopping

Press **Ctrl+C** to stop monitoring. You'll see a final summary:

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

## Troubleshooting

### "Log file not found"

This is normal! The analyzer will wait for the file to be created. Just start your model service or run a simulation.

### No alerts appearing

1. Check model service is running: `curl http://localhost:8000/`
2. Verify predictions are being logged: `ls -lh logs/`
3. Try more sensitive detection: `--delta 0.001`
4. Check window size matches your data volume

### Too many false alarms

Increase delta for less sensitivity:
```bash
python realtime_drift_analyzer.py --auto --delta 0.01
```

## Next Steps

- Read full guide: [REALTIME_ANALYZER_GUIDE.md](REALTIME_ANALYZER_GUIDE.md)
- Compare with batch detector: [README.md](README.md)
- See implementation details: [REALTIME_ANALYZER_SUMMARY.md](REALTIME_ANALYZER_SUMMARY.md)
