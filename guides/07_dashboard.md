# Guide: Visualization Dashboard

## Overview

This guide covers using the Streamlit dashboard to visualize drift detection results with interactive charts.

## Prerequisites

- ✅ Prediction logs exist (`logs/predictions_*.jsonl`)
- ✅ Optional: Drift detection results
- ✅ Optional: Window metadata

## Quick Start

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at http://localhost:8501

## Dashboard Features

### 1. File Selection

**Sidebar → Select Log File**

- Dropdown lists all available prediction log files
- Automatically selects most recent file
- Updates all visualizations when changed

### 2. Feature Distribution Visualization

**Main Panel → Feature Over Time**

- Time series plot of selected feature values
- Red dashed lines mark detected drift points
- Hover for detailed information
- Zoom and pan capabilities

**Main Panel → Feature Distribution**

- Histogram of feature value distribution
- Shows frequency of different values
- Updates based on time range filter

### 3. Drift Detection Results

**Main Panel → Drift Statistic Over Time**

- Line chart showing drift statistic per window
- Red points = Drift detected
- Green points = No drift
- Gray horizontal line = Baseline mean

**Main Panel → Detection vs Ground Truth**

- Bar chart comparing detection results
- Shows True Positives, False Positives, etc.
- Only visible when ground truth available
- Accuracy metrics displayed

### 4. Time Range Filtering

**Sidebar → Time Range**

- Slider to select window range
- Filters all visualizations
- Shows start and end window IDs
- Updates charts in real-time

### 5. Data Details

**Expandable Sections**

- **View Predictions Data**: First 100 predictions
- **View Detection Results**: First 20 detection windows
- Sortable columns
- Searchable content

## Using the Dashboard

### Basic Workflow

1. **Start Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

2. **Select Log File**
   - Use dropdown in sidebar
   - Pick the simulation run you want to analyze

3. **Choose Feature**
   - Select from dropdown (feature1, feature2, feature3)
   - View time series and distribution

4. **Analyze Drift**
   - Look for red vertical lines (drift points)
   - Check drift statistic chart
   - Compare with ground truth

5. **Filter Time Range**
   - Use slider to zoom into specific windows
   - Focus on areas of interest

### Example Analysis Session

**Scenario**: Analyze simple drift simulation

1. **Run Simulation**
   ```bash
   python src/drift_simulator.py --config configs/config_simple.json
   python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl
   ```

2. **Open Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

3. **Observations**
   - Windows 0-1: Stable (baseline)
   - Windows 2-3: Drift detected
   - Features show clear distribution shift
   - Accuracy metrics show detection performance

## Dashboard Configuration

### Change Port

```bash
streamlit run dashboard.py --server.port 8502
```

### Run on Different Host

```bash
streamlit run dashboard.py --server.address 0.0.0.0
```

### Disable Auto-Refresh

```bash
streamlit run dashboard.py --server.runOnSave false
```

## Data Requirements

### Minimum Requirements

**Required:**
- At least one prediction log file in `logs/`

**Optional but Recommended:**
- `outputs/metadata/window_metadata.json` - Ground truth labels
- `outputs/detection/drift_detection.json` - Detection results

### File Locations

The dashboard looks for files in these locations:

```
logs/
└── predictions_*.jsonl       # Required

outputs/
├── metadata/
│   └── window_metadata.json  # Optional (for ground truth)
└── detection/
    └── drift_detection.json  # Optional (for drift results)
```

## Visualization Details

### Feature Time Series

**X-axis**: Timestamp
**Y-axis**: Feature value
**Markers**: Individual predictions
**Line**: Connecting points for trend
**Red dashed lines**: Drift detection points

**Interactions:**
- Hover: See exact values
- Zoom: Drag to select area
- Pan: Shift + drag
- Reset: Double-click

### Feature Distribution

**X-axis**: Feature value bins
**Y-axis**: Count/frequency
**Bars**: Histogram bins (30 bins by default)

**Shows:**
- Value distribution shape
- Outliers
- Multi-modal distributions

### Drift Statistic Chart

**X-axis**: Timestamp
**Y-axis**: Drift statistic value
**Colors**:
- Red points: Drift detected
- Green points: No drift
**Gray line**: Baseline mean reference

### Detection Comparison

**Bars**: Count of each detection type
**Colors**:
- Green: True Positive / True Negative
- Red: False Positive
- Salmon: False Negative

## Performance Tips

### Large Log Files

For files with >10,000 predictions:

1. Use time range filter to view subsets
2. Consider downsampling for visualization
3. Use batch analysis for processing

### Multiple Files

Dashboard loads one file at a time. To compare:

1. Run dashboard multiple times on different ports
2. Or analyze separately and compare results

### Slow Loading

If dashboard is slow:

1. Check file sizes (`ls -lh logs/`)
2. Use smaller time ranges
3. Close other browser tabs
4. Restart streamlit

## Troubleshooting

### Error: "No prediction log files found"

**Solution**: Run a simulation first
```bash
python src/drift_simulator.py --config configs/config_simple.json
```

### Charts Not Showing

**Possible Causes:**
1. No data in selected range → Adjust time range slider
2. Invalid JSON in log file → Validate with `jq`
3. Feature not in data → Check available features

**Debug:**
```bash
# Validate log file
cat logs/predictions_20251214.jsonl | jq . > /dev/null && echo "Valid JSON"

# Check features
cat logs/predictions_20251214.jsonl | head -1 | jq '.input_features | keys'
```

### Ground Truth Not Available

This is normal if you didn't run simulation. The dashboard will work without it:
- No ground truth comparison chart
- No accuracy metrics
- Still shows all other features

### Dashboard Crashes

**Solution**: Check for errors in log files
```bash
# Check for malformed JSON
cat logs/predictions_20251214.jsonl | while read line; do
  echo "$line" | jq . > /dev/null || echo "Invalid: $line"
done
```

## Customization

### Add New Visualizations

Edit `dashboard.py` to add custom charts:

```python
import plotly.express as px

# Add custom chart
fig = px.scatter(df, x='timestamp', y='prediction', color='drift_detected')
st.plotly_chart(fig, use_container_width=True)
```

### Change Color Scheme

```python
# In dashboard.py
fig.update_traces(marker_color='blue')  # Change color
```

### Add New Metrics

```python
# Calculate custom metric
metric_value = df['prediction'].quantile(0.95)
st.metric("95th Percentile", f"{metric_value:.4f}")
```

## Sharing Results

### Export Charts

1. Hover over chart
2. Click camera icon (top right)
3. Save as PNG

### Share Dashboard

**Option 1**: Screen recording
```bash
# Record your screen while navigating dashboard
```

**Option 2**: Deploy to Streamlit Cloud
```bash
# Follow Streamlit Cloud documentation
```

**Option 3**: Generate Static Report
```python
# Use plotly to save charts
import plotly.io as pio
pio.write_html(fig, file='drift_report.html')
```

## Advanced Features

### Multi-Feature Comparison

View multiple features:
1. Select feature1 → Take screenshot
2. Select feature2 → Take screenshot
3. Select feature3 → Take screenshot
4. Compare side-by-side

### Time Series Analysis

Identify patterns:
- Periodic drift (cyclic)
- Gradual drift (trend)
- Abrupt drift (step change)

### Statistical Insights

Use data details section:
- Export to CSV
- Run custom analysis in Python
- Compare statistics across windows

## Integration with Analysis Workflow

### Complete Analysis Pipeline

```bash
# 1. Run simulation
python src/drift_simulator.py --config configs/config_simple.json

# 2. Detect drift (batch)
python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl

# 3. Analyze statistics
python analyze_drift.py --log-file logs/predictions_$(date +%Y%m%d).jsonl

# 4. Visualize in dashboard
streamlit run dashboard.py
```

### Real-Time + Dashboard

Use both tools together:

**Terminal 1**: Real-time monitoring
```bash
python realtime_drift_analyzer.py --auto
```

**Terminal 2**: Dashboard for post-analysis
```bash
streamlit run dashboard.py
```

## Best Practices

### 1. Always Run Drift Detection First

Dashboard works better with detection results:
```bash
python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl
streamlit run dashboard.py
```

### 2. Use Time Range Filter

For large datasets, filter to area of interest:
- Baseline period only
- Drift period only
- Specific incident time

### 3. Compare Features

Check all three features to understand drift:
- Which features drifted?
- How much did they change?
- Are changes correlated?

### 4. Validate with Ground Truth

If available, always check accuracy metrics:
- Is detection reliable?
- What's the false positive rate?
- Are we missing drift?

## Next Steps

After exploring the dashboard:

1. ✅ Insights gained → Adjust detection parameters
   - Tune delta for better accuracy
   - Change window size for granularity

2. ✅ Patterns identified → Investigate root causes
   - What caused the drift?
   - Can it be prevented?

3. ✅ Validated results → Deploy to production
   - Use real-time analyzer
   - Monitor ongoing drift

## Related Guides

- [Drift Simulation](04_drift_simulation.md) - Generate data
- [Batch Detection](05_batch_detection.md) - Detect drift
- [Real-Time Detection](06_realtime_detection.md) - Live monitoring

## Additional Resources

- **dashboard.py**: Dashboard source code
- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python/
