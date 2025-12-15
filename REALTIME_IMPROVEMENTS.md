# Real-Time Analyzer Improvements

## Issues Fixed

### Issue 1: Window ID Always Shows 0

**Problem**: All windows were labeled as "Window 0" instead of incrementing properly.

**Root Cause**: The `window.clear()` method (which increments `window_id`) was never being called after analyzing a window.

**Fix**:
- Added `self.window.clear()` call after creating the alert in `_analyze_window()` (line 212)
- Changed to use `self.total_windows` as the window ID (line 196) since it gets incremented after

**Result**: Windows now properly show as Window 0, Window 1, Window 2, etc.

---

### Issue 2: Low Drift Detection Rate (Only Phase Transitions Detected)

**Problem**: Only 3 drift detections out of 1401 windows analyzed (0.2%), missing most drift periods.

**Root Cause**: ADWIN algorithm detects **changes** between consecutive windows, not absolute drift from baseline. So during a stable drift period (e.g., all predictions around 0.5 when baseline is 0.08), ADWIN sees no change between consecutive windows and reports no drift.

**Example**:
```
Window 0: mean=0.08 (baseline) → No drift
Window 1: mean=0.09            → ADWIN: No drift (small change)
Window 2: mean=0.50            → ADWIN: DRIFT! (big change from window 1)
Window 3: mean=0.51            → ADWIN: No drift (small change from window 2)
Window 4: mean=0.52            → ADWIN: No drift (small change from window 3)
...
```

Only window 2 (the transition) is detected, even though windows 3-N are all drifted from baseline.

**Fix**: Added dual drift detection mechanism (lines 180-189):

1. **ADWIN Drift**: Detects changes between consecutive windows (existing behavior)
2. **Baseline Drift**: Detects absolute difference from baseline using threshold

```python
# ADWIN detects changes between windows
adwin_drift = self.adwin.drift_detected

# Baseline check detects absolute drift from baseline
threshold = self.delta * 50  # 0.002 * 50 = 0.1 (10% threshold)
baseline_drift = drift_statistic > threshold

# Flag drift if either detector triggers
drift_detected = adwin_drift or baseline_drift
```

**Threshold Calculation**:
- Default delta: 0.002
- Threshold: `delta * 50 = 0.1` (10% of baseline)
- Example: If baseline=0.08, drift flagged when |current_mean - 0.08| > 0.1

**Alert Message Enhancement**:
Drift alerts now show which detector(s) triggered:
- `🚨 DRIFT DETECTED [ADWIN]!` - ADWIN detected change
- `🚨 DRIFT DETECTED [Baseline]!` - Baseline threshold exceeded
- `🚨 DRIFT DETECTED [ADWIN, Baseline]!` - Both detectors triggered

---

## Testing

### Test Case 1: Window ID Increment
```python
detector = RealtimeDriftDetector(window_size=5)
# Process 15 predictions (3 windows)
# Result: Window 0, Window 1, Window 2 ✓
```

### Test Case 2: Baseline Drift Detection
```python
detector = RealtimeDriftDetector(window_size=5, delta=0.002)
# Window 0: mean=0.12 (baseline)
# Window 1: mean=0.12 (no drift)
# Window 2: mean=0.52 (drift: |0.52-0.12| = 0.40 > 0.1)
# Result: Drift detected in Window 2 ✓
```

### Expected Behavior with config_complex.json

With the simulation config that has phases:
1. **Baseline** (500 predictions, 5 windows): No drift
2. **Gradual Drift** (400 predictions, 4 windows):
   - First window: ADWIN detects transition
   - Remaining windows: Baseline detector flags ongoing drift
3. **Stable High** (200 predictions, 2 windows): Baseline detector flags drift
4. **Abrupt Drift** (400 predictions, 4 windows):
   - First window: Both detectors trigger
   - Remaining windows: Baseline detector flags drift

**Expected drift rate**: ~70-80% (11-12 out of 15 windows) instead of previous 0.2%

---

## Configuration

### Adjusting Baseline Drift Threshold

If you want to make baseline drift detection more or less sensitive:

```python
# In _analyze_window(), line 186
threshold = self.delta * 50  # Current: 10% threshold

# More sensitive (5% threshold):
threshold = self.delta * 25

# Less sensitive (20% threshold):
threshold = self.delta * 100
```

Or add a new CLI parameter:
```bash
python realtime_drift_analyzer.py --auto --baseline-threshold 0.05
```

---

## Files Modified

1. **realtime_drift_analyzer.py**:
   - Line 186-189: Added baseline drift detection
   - Line 196: Use `total_windows` for window ID
   - Line 205: Pass `adwin_drift` and `baseline_drift` to alert message
   - Line 212: Call `window.clear()` after analysis
   - Line 216-241: Updated `_create_alert_message()` signature and implementation

---

## Impact

### Before
- ❌ Window IDs always showed 0
- ❌ Only detected drift at phase transitions (0.2% detection rate)
- ❌ Missed ongoing drift periods

### After
- ✅ Window IDs increment correctly (0, 1, 2, ...)
- ✅ Detects both transitions and ongoing drift (70-80% detection rate expected)
- ✅ Shows which detector(s) triggered the alert
- ✅ More accurate representation of drift state

---

## Next Steps

1. Test with your simulation:
   ```bash
   # Terminal 1
   python realtime_drift_analyzer.py --auto

   # Terminal 2
   python src/drift_simulator.py --config configs/config_complex.json
   ```

2. Expected output:
   - Windows should show: Window 0, Window 1, Window 2, etc.
   - Drift detection should be much higher (~70-80% instead of 0.2%)
   - Alerts should show `[ADWIN]`, `[Baseline]`, or `[ADWIN, Baseline]`

3. Tune threshold if needed:
   - Too many false positives → increase threshold (line 186)
   - Missing drift → decrease threshold (line 186)
