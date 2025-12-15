# Guide: Real-Time Drift Detection

## Overview

This guide covers monitoring prediction logs in real-time and getting immediate drift alerts using the file-tailing approach.

> **📖 Full Documentation**: See [REALTIME_ANALYZER_GUIDE.md](../REALTIME_ANALYZER_GUIDE.md) for comprehensive details.

## Prerequisites

- ✅ `watchdog` library installed (`pip install watchdog==3.0.0`)
- ✅ Prediction logs being generated

## Quick Start

```bash
# Auto-detect today's log file
python realtime_drift_analyzer.py --auto
```

## Common Use Cases

### Monitor Live Predictions

**Terminal 1**: Model Service
```bash
python src/model_service.py
```

**Terminal 2**: Real-Time Analyzer
```bash
python realtime_drift_analyzer.py --auto
```

**Terminal 3**: Generate Predictions
```bash
python src/drift_simulator.py --config configs/config_simple.json
```

Watch Terminal 2 for real-time drift alerts!

### Monitor Specific File

```bash
python realtime_drift_analyzer.py --log-file logs/predictions_20251214.jsonl
```

### Faster Detection (Smaller Window)

```bash
python realtime_drift_analyzer.py --auto --window-size 50
```

### More Sensitive Detection

```bash
python realtime_drift_analyzer.py --auto --delta 0.001
```

### Quiet Mode (Only Alerts)

```bash
python realtime_drift_analyzer.py --auto --quiet
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--auto` | - | Auto-detect today's log file |
| `--log-file` | - | Specific log file to monitor |
| `--window-size` | 100 | Predictions per window |
| `--delta` | 0.002 | ADWIN sensitivity (0.001-0.01) |
| `--quiet` | False | Only show drift alerts |

## What You'll See

### Drift Alert

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

### Normal Window

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

### Status Update (Every 60s)

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

### Final Summary (Ctrl+C)

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

1. **File Monitoring**: Uses `watchdog` to detect file changes
2. **Tail Behavior**: Only reads new lines (like `tail -f`)
3. **Sliding Window**: Maintains buffer of recent predictions
4. **ADWIN Detection**: Processes each prediction immediately
5. **Immediate Alerts**: Prints to console when drift detected

## Testing

Quick test with simulated drift:

**Terminal 1**: Start analyzer
```bash
python realtime_drift_analyzer.py --log-file logs/test_realtime.jsonl --window-size 10
```

**Terminal 2**: Run test
```bash
python tests/test_realtime.py
```

Expected: You'll see drift detected in Terminal 1 after ~20 baseline predictions.

## Tuning Parameters

### Window Size

**Small (50)**: Faster detection, more sensitive
```bash
python realtime_drift_analyzer.py --auto --window-size 50
```

**Large (200)**: Slower detection, more stable
```bash
python realtime_drift_analyzer.py --auto --window-size 200
```

### Delta (Sensitivity)

**More Sensitive (0.001)**: Detect smaller changes
```bash
python realtime_drift_analyzer.py --auto --delta 0.001
```

**Less Sensitive (0.01)**: Only large changes
```bash
python realtime_drift_analyzer.py --auto --delta 0.01
```

## Comparison: Real-Time vs Batch

| Aspect | Real-Time | Batch |
|--------|-----------|-------|
| **Latency** | Seconds | Minutes to hours |
| **Use Case** | Live monitoring | Post-hoc analysis |
| **Output** | Console alerts | JSON files |
| **Ground Truth** | No | Yes (if available) |
| **Metrics** | Drift count, rate | Precision, recall, accuracy |
| **Best For** | Production monitoring | Research & validation |

## When to Use Real-Time Detection

**Use real-time when:**
- ✅ Need immediate alerts
- ✅ Monitoring production systems
- ✅ Want to see drift as it happens
- ✅ Console output is sufficient

**Use batch when:**
- ✅ Need detailed analysis
- ✅ Want ground truth comparison
- ✅ Analyzing historical data
- ✅ Need precision/recall metrics

## Troubleshooting

### No Alerts Appearing

**Possible Causes:**
1. No predictions being logged → Check model service
2. Window not complete → Need 100 predictions (default)
3. No drift in data → Check with batch analyzer
4. Delta too high → Try `--delta 0.001`

### Too Many False Alarms

**Solution**: Increase delta
```bash
python realtime_drift_analyzer.py --auto --delta 0.01
```

### Log File Not Found

This is normal! Analyzer waits for file creation. Just start your model service.

## Best Practices

### 1. Run Alongside Batch Detection

Use both for different insights:
- Real-time: Immediate alerts
- Batch: Detailed analysis

### 2. Start with Default Parameters

```bash
python realtime_drift_analyzer.py --auto
```

Then tune based on results.

### 3. Use Quiet Mode in Production

```bash
python realtime_drift_analyzer.py --auto --quiet > drift_alerts.log 2>&1
```

### 4. Monitor Multiple Sessions

Use different terminals for different log files.

## Integration Examples

### With Model Service

```bash
# Start both in background
python src/model_service.py &
python realtime_drift_analyzer.py --auto &
```

### With Simulation

Perfect for testing:
```bash
python realtime_drift_analyzer.py --auto --window-size 10 &
python src/drift_simulator.py --config configs/config_simple.json
```

### Save Alerts to File

```bash
python realtime_drift_analyzer.py --auto 2>&1 | tee drift_alerts.log
```

## Architecture

```
Model Service → JSONL Log → Watchdog → Real-Time Analyzer
                                  ↓
                            Sliding Window
                                  ↓
                            ADWIN Detection
                                  ↓
                            Console Alerts
```

## Performance

**Latency:** 10-500ms from log write to detection
**Memory:** ~1-10MB (depends on window size)
**CPU:** <1% idle, 5-10% active
**Optimal:** 1-100 predictions/second

## Next Steps

After setting up real-time monitoring:

1. ✅ Alerts working → Integrate with production
   - Add to monitoring dashboard
   - Set up webhooks (future enhancement)

2. ✅ Parameters tuned → Validate with batch
   - Compare real-time vs batch results
   - Verify detection accuracy

3. ✅ Running smoothly → Explore enhancements
   - Multiple log files
   - Custom alert destinations
   - Metrics export

## Related Guides

- [Batch Drift Detection](05_batch_detection.md) - Detailed analysis
- [Drift Simulation](04_drift_simulation.md) - Generate test data
- [Dashboard Guide](07_dashboard.md) - Visualize results

## Full Documentation

For comprehensive documentation including:
- Architecture details
- Alert callback integration
- Advanced configuration
- Troubleshooting guide
- Performance characteristics
- Future enhancements

See: [REALTIME_ANALYZER_GUIDE.md](../REALTIME_ANALYZER_GUIDE.md)

## Quick Reference

```bash
# Basic usage
python realtime_drift_analyzer.py --auto

# Custom parameters
python realtime_drift_analyzer.py --log-file <file> --window-size <N> --delta <D>

# Quiet mode
python realtime_drift_analyzer.py --auto --quiet

# Help
python realtime_drift_analyzer.py --help
```

**Press Ctrl+C to stop and see summary.**
