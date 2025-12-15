# Guide: Batch Drift Detection

## Overview

This guide covers using the batch drift detector to analyze prediction logs and detect drift using the ADWIN algorithm.

## Prerequisites

- ✅ Prediction logs generated (`logs/predictions_*.jsonl`)
- ✅ Optional: Window metadata from simulation

## Quick Start

```bash
# Auto-detect today's log file
python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl
```

## Command-Line Options

```bash
python src/drift_detector.py [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--log-file` | (required) | Path to predictions JSONL file |
| `--metadata` | outputs/metadata/window_metadata.json | Path to window metadata |
| `--window-size` | 100 | Predictions per window |
| `--delta` | 0.002 | ADWIN sensitivity (0.001-0.01) |
| `--output` | outputs/detection/drift_detection.json | Output file path |

## Basic Usage

### Detect with Defaults

```bash
python src/drift_detector.py --log-file logs/predictions_20251214.jsonl
```

### With Ground Truth

```bash
python src/drift_detector.py \
  --log-file logs/predictions_20251214.jsonl \
  --metadata outputs/metadata/window_metadata.json
```

### Custom Parameters

```bash
python src/drift_detector.py \
  --log-file logs/predictions_20251214.jsonl \
  --window-size 50 \
  --delta 0.001 \
  --output outputs/my_detection.json
```

## Expected Output

```
======================================================================
Drift Detection Engine - Epic 3
======================================================================
Configuration:
  Window size: 100
  ADWIN delta: 0.002
  Total predictions: 400

Created 4 windows

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
Detection rate: 25.0%

Ground Truth Comparison:
  Accuracy: 75.0% (3/4)
  True Positives:  1
  False Positives: 0
  True Negatives:  2
  False Negatives: 1
  Precision: 1.00
  Recall: 0.50

✓ Drift detection results saved to outputs/detection/drift_detection.json
  Total windows analyzed: 4
```

## Output Format

**File**: `outputs/detection/drift_detection.json`

**Structure**: Array of detection results

```json
[
  {
    "window_id": 0,
    "timestamp": "2025-12-14T20:45:37.234567Z",
    "drift_statistic": 0.0,
    "drift_detected": false,
    "adwin_detected": false,
    "baseline_mean": 0.071059,
    "current_mean": 0.071059,
    "current_std": 0.085500,
    "predictions_processed": 100,
    "ground_truth_drift": false
  },
  {
    "window_id": 2,
    "timestamp": "2025-12-14T20:45:52.456789Z",
    "drift_statistic": 0.429292,
    "drift_detected": true,
    "adwin_detected": true,
    "baseline_mean": 0.071059,
    "current_mean": 0.500350,
    "current_std": 0.320717,
    "predictions_processed": 100,
    "ground_truth_drift": true
  }
]
```

## Understanding Results

### Drift Statistics

**Drift Statistic** = |current_mean - baseline_mean|

- **0.0 - 0.05**: Minimal drift
- **0.05 - 0.2**: Moderate drift
- **0.2 - 0.5**: Significant drift
- **> 0.5**: Severe drift

### Detection Flags

- **drift_detected**: Overall drift detected (ADWIN or statistic-based)
- **adwin_detected**: ADWIN algorithm specifically detected drift
- **ground_truth_drift**: True drift from simulation (if available)

### Accuracy Metrics

When ground truth is available:

- **True Positive**: Correctly detected drift
- **False Positive**: Detected drift when there was none
- **True Negative**: Correctly detected no drift
- **False Negative**: Missed actual drift

**Precision** = TP / (TP + FP) - How many detections were correct?
**Recall** = TP / (TP + FN) - How many actual drifts were detected?

## Tuning ADWIN Delta

The `delta` parameter controls sensitivity:

### More Sensitive (Lower Delta)

```bash
python src/drift_detector.py --log-file logs/predictions_20251214.jsonl --delta 0.0001
```

**Effect:**
- Detects smaller changes
- More drift detections
- Higher false positive rate
- Better recall, lower precision

**Use when:**
- Need to catch subtle drift
- False positives acceptable
- Early detection critical

### Less Sensitive (Higher Delta)

```bash
python src/drift_detector.py --log-file logs/predictions_20251214.jsonl --delta 0.01
```

**Effect:**
- Detects only significant changes
- Fewer drift detections
- Lower false positive rate
- Lower recall, better precision

**Use when:**
- Only major drift matters
- False positives costly
- Stable operation desired

### Recommended Values

| Scenario | Delta | Description |
|----------|-------|-------------|
| Development/Testing | 0.002 | Balanced (default) |
| Subtle Drift Detection | 0.0001-0.001 | High sensitivity |
| Production Monitoring | 0.002-0.005 | Moderate sensitivity |
| Critical Systems | 0.005-0.01 | Low false positives |

## Window Size Considerations

### Small Windows (50-100)

```bash
python src/drift_detector.py --log-file logs/predictions_20251214.jsonl --window-size 50
```

**Pros:**
- Faster detection
- More granular analysis
- Better for rapid drift

**Cons:**
- More noise sensitivity
- Higher false positive rate
- Needs more windows

### Large Windows (200-500)

```bash
python src/drift_detector.py --log-file logs/predictions_20251214.jsonl --window-size 200
```

**Pros:**
- More stable statistics
- Lower false positive rate
- Better for gradual drift

**Cons:**
- Slower detection
- May miss rapid changes
- Fewer data points

## Analyzing Multiple Files

### Batch Processing Script

```bash
#!/bin/bash
# analyze_all_logs.sh

for log_file in logs/predictions_*.jsonl; do
  echo "Processing $log_file..."

  output_file="outputs/detection/$(basename $log_file .jsonl)_detection.json"

  python src/drift_detector.py \
    --log-file "$log_file" \
    --output "$output_file"

  echo "Results saved to $output_file"
  echo "---"
done
```

### Comparing Results

```bash
# Compare detection rates
for file in outputs/detection/*.json; do
  echo -n "$(basename $file): "
  jq '[.[] | select(.drift_detected)] | length' "$file"
done
```

## Integrating with Python

### Example: Programmatic Detection

```python
from pathlib import Path
from src.drift_detector import DriftDetector

# Initialize detector
detector = DriftDetector(window_size=100, delta=0.002)

# Load and process
predictions = detector.load_predictions('logs/predictions_20251214.jsonl')
metadata = detector.load_window_metadata('outputs/metadata/window_metadata.json')

# Detect drift
detector.process_all_windows(predictions, metadata)

# Save results
detector.save_results('outputs/detection/my_results.json')

# Get summary
summary = detector.get_summary()
print(f"Drift detected in {summary['drift_count']} windows")
```

### Example: Custom Analysis

```python
import json
from pathlib import Path

# Load detection results
with open('outputs/detection/drift_detection.json', 'r') as f:
    results = json.load(f)

# Find all drift points
drift_points = [r for r in results if r['drift_detected']]

# Calculate average drift magnitude
if drift_points:
    avg_drift = sum(r['drift_statistic'] for r in drift_points) / len(drift_points)
    print(f"Average drift magnitude: {avg_drift:.4f}")

# Find largest drift
max_drift = max(results, key=lambda x: x['drift_statistic'])
print(f"Largest drift at window {max_drift['window_id']}: {max_drift['drift_statistic']:.4f}")
```

## Troubleshooting

### Error: "Log file not found"

**Solution**: Check file path
```bash
ls -l logs/
python src/drift_detector.py --log-file logs/predictions_20251214.jsonl
```

### No Drift Detected

**Possible Causes:**
1. Delta too high → Try `--delta 0.001`
2. No actual drift in data
3. Drift too subtle

**Debug:**
```bash
python analyze_drift.py --log-file logs/predictions_20251214.jsonl
```

### All Windows Show Drift

**Possible Causes:**
1. Delta too low → Try `--delta 0.01`
2. Noisy data
3. Actual drift throughout

**Solution**: Tune delta or check data quality

### Mismatch with Ground Truth

**This is normal!** ADWIN detects **changes**, not **states**:

- Window 2: Drift starts → DRIFT (correct)
- Window 3: Still drifted → STABLE (ADWIN adapted)

This is expected behavior. ADWIN detects the *point of change*, not the ongoing drifted state.

## Best Practices

### 1. Start with Defaults

```bash
python src/drift_detector.py --log-file logs/predictions_20251214.jsonl
```

### 2. Tune Based on Results

If too many false positives → Increase delta
If missing drift → Decrease delta

### 3. Validate with Ground Truth

Always run with metadata when available:
```bash
--metadata outputs/metadata/window_metadata.json
```

### 4. Save Results

Always specify output file for reproducibility:
```bash
--output outputs/detection/experiment_001.json
```

### 5. Document Parameters

Keep a log of parameters used:
```bash
echo "$(date): delta=0.002, window=100" >> detection_log.txt
```

## Next Steps

After drift detection:

1. ✅ Results generated → Visualize in dashboard
   - See [Dashboard Guide](07_dashboard.md)

2. ✅ Drift patterns identified → Investigate causes
   - Analyze feature distributions
   - Compare with ground truth

3. ✅ Parameters tuned → Run on production data
   - Apply to real prediction logs
   - Monitor ongoing drift

## Related Guides

- [Drift Simulation](04_drift_simulation.md)
- [Real-Time Detection](06_realtime_detection.md)
- [Dashboard Guide](07_dashboard.md)

## Additional Resources

- **src/drift_detector.py**: Detector source code
- **analyze_drift.py**: Statistical analysis tool
- **README.md**: Project overview
