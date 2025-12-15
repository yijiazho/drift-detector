# Drift Detection System - User Guides

## Overview

This directory contains comprehensive, step-by-step guides for all components of the Drift Detection System. Each guide focuses on a specific use case or workflow.

## Quick Navigation

### Getting Started (5 minutes)

1. **[Creating the Model](01_creating_model.md)** - Create the pre-fitted logistic regression model
2. **[Model Service](02_model_service.md)** - Start the FastAPI prediction service
3. **[Making Predictions](03_predictions.md)** - Make predictions with the model

### Running Experiments (15 minutes)

4. **[Drift Simulation](04_drift_simulation.md)** - Generate synthetic data with drift patterns

### Analyzing Results (10 minutes)

5. **[Batch Drift Detection](05_batch_detection.md)** - Analyze logs and detect drift offline
6. **[Real-Time Drift Detection](06_realtime_detection.md)** - Monitor predictions and detect drift live
7. **[Visualization Dashboard](07_dashboard.md)** - Explore results with interactive charts

## Guide Overview

| Guide | Time | Level | Prerequisites |
|-------|------|-------|---------------|
| [Creating the Model](01_creating_model.md) | 2 min | Beginner | None |
| [Model Service](02_model_service.md) | 5 min | Beginner | Model created |
| [Making Predictions](03_predictions.md) | 5 min | Beginner | Service running |
| [Drift Simulation](04_drift_simulation.md) | 10 min | Intermediate | Service running |
| [Batch Detection](05_batch_detection.md) | 5 min | Intermediate | Logs generated |
| [Real-Time Detection](06_realtime_detection.md) | 10 min | Advanced | Logs being generated |
| [Dashboard](07_dashboard.md) | 10 min | Beginner | Logs exist |

## Common Workflows

### Workflow 1: Quick Test (15 minutes)

**Goal**: Test the complete system end-to-end

```bash
# 1. Create model (2 min)
python create_model.py

# 2. Start service (Terminal 1)
python src/model_service.py

# 3. Run simulation (Terminal 2)
python src/drift_simulator.py --config configs/config_simple.json

# 4. Detect drift
python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl

# 5. Visualize
streamlit run dashboard.py
```

**Guides**: [01](01_creating_model.md) → [02](02_model_service.md) → [04](04_drift_simulation.md) → [05](05_batch_detection.md) → [07](07_dashboard.md)

---

### Workflow 2: Production Monitoring (Ongoing)

**Goal**: Monitor real production predictions for drift

```bash
# 1. Start service (background)
python src/model_service.py &

# 2. Start real-time analyzer (background)
python realtime_drift_analyzer.py --auto --quiet > drift_alerts.log 2>&1 &

# 3. Your application makes predictions
# POST http://localhost:8000/predict

# 4. Check alerts
tail -f drift_alerts.log
```

**Guides**: [02](02_model_service.md) → [03](03_predictions.md) → [06](06_realtime_detection.md)

---

### Workflow 3: Research & Validation (1 hour)

**Goal**: Validate drift detection accuracy with ground truth

```bash
# 1. Run multiple simulations with different configurations
for config in configs/*.json; do
  python src/drift_simulator.py --config "$config"
  python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl
done

# 2. Compare results
python analyze_drift.py --log-file logs/predictions_$(date +%Y%m%d).jsonl

# 3. Visualize and analyze
streamlit run dashboard.py
```

**Guides**: [04](04_drift_simulation.md) → [05](05_batch_detection.md) → [07](07_dashboard.md)

---

### Workflow 4: Custom Drift Scenarios (30 minutes)

**Goal**: Test specific drift patterns

```bash
# 1. Create custom configuration
cat > configs/my_scenario.json << EOF
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
      "name": "my_drift",
      "num_requests": 200,
      "is_drift": true,
      "drift_type": "abrupt",
      "distribution": {
        "feature1": {"mean": 7.0, "std": 1.0},
        "feature2": {"mean": 2.8, "std": 0.5},
        "feature3": {"mean": 1.9, "std": 0.3}
      }
    }
  ]
}
EOF

# 2. Run simulation
python src/drift_simulator.py --config configs/my_scenario.json

# 3. Analyze
python src/drift_detector.py --log-file logs/predictions_$(date +%Y%m%d).jsonl
streamlit run dashboard.py
```

**Guides**: [04](04_drift_simulation.md) → [05](05_batch_detection.md) → [07](07_dashboard.md)

## Learning Path

### Beginner Path

1. ✅ Read [Creating the Model](01_creating_model.md)
2. ✅ Read [Model Service](02_model_service.md)
3. ✅ Follow Quick Test workflow above
4. ✅ Explore [Dashboard](07_dashboard.md)

**Time**: 30 minutes
**Outcome**: Understand basic system operation

### Intermediate Path

1. ✅ Complete Beginner Path
2. ✅ Read [Drift Simulation](04_drift_simulation.md)
3. ✅ Read [Batch Detection](05_batch_detection.md)
4. ✅ Create custom drift scenario
5. ✅ Analyze results

**Time**: 1 hour
**Outcome**: Understand drift detection mechanics

### Advanced Path

1. ✅ Complete Intermediate Path
2. ✅ Read [Real-Time Detection](06_realtime_detection.md)
3. ✅ Set up production monitoring
4. ✅ Tune ADWIN parameters
5. ✅ Compare batch vs real-time

**Time**: 2 hours
**Outcome**: Production-ready monitoring setup

## Quick Reference

### File Locations

```
drift-detector/
├── guides/                      # You are here
│   ├── README.md               # This file
│   ├── 01_creating_model.md
│   ├── 02_model_service.md
│   ├── 03_predictions.md
│   ├── 04_drift_simulation.md
│   ├── 05_batch_detection.md
│   ├── 06_realtime_detection.md
│   └── 07_dashboard.md
├── configs/                     # Drift scenario configurations
├── models/                      # Trained models
├── logs/                        # Prediction logs
├── outputs/                     # Detection results
└── src/                         # Source code
```

### Common Commands

```bash
# Setup
python create_model.py
pip install -r requirements.txt

# Run
python src/model_service.py
python src/drift_simulator.py --config configs/config_simple.json
python src/drift_detector.py --log-file logs/predictions_YYYYMMDD.jsonl
python realtime_drift_analyzer.py --auto
streamlit run dashboard.py

# Test
python test_service.py
python tests/test_integration.py
python tests/test_realtime.py

# Analyze
python analyze_drift.py --log-file logs/predictions_YYYYMMDD.jsonl
```

## Getting Help

### By Topic

| Topic | See Guide | Section |
|-------|-----------|---------|
| Model not loading | [Model Service](02_model_service.md) | Troubleshooting |
| Predictions failing | [Making Predictions](03_predictions.md) | Error Handling |
| No drift detected | [Batch Detection](05_batch_detection.md) | Troubleshooting |
| Too many alerts | [Real-Time Detection](06_realtime_detection.md) | Tuning Parameters |
| Dashboard errors | [Dashboard](07_dashboard.md) | Troubleshooting |

### Common Issues

**Q: Model file not found**
A: Run `python create_model.py` first. See [Guide 01](01_creating_model.md)

**Q: Port 8000 in use**
A: Kill existing process or use different port. See [Guide 02](02_model_service.md#troubleshooting)

**Q: No drift detected**
A: Tune delta parameter or check data. See [Guide 05](05_batch_detection.md#tuning-adwin-delta)

**Q: Too many false positives**
A: Increase delta or window size. See [Guide 06](06_realtime_detection.md#tuning-parameters)

## Additional Resources

### Comprehensive Guides

- **[REALTIME_ANALYZER_GUIDE.md](../REALTIME_ANALYZER_GUIDE.md)** - Deep dive into real-time monitoring
- **[README.md](../README.md)** - Project overview and quick start
- **[EPIC5_IMPLEMENTATION.md](../EPIC5_IMPLEMENTATION.md)** - Schema and integration details

### Quick References

- **[QUICKSTART_REALTIME.md](../QUICKSTART_REALTIME.md)** - Real-time analyzer quick reference
- **[TEST_PLAN_SUMMARY.md](../TEST_PLAN_SUMMARY.md)** - Testing guide

### Technical Documentation

- **[REALTIME_ANALYZER_SUMMARY.md](../REALTIME_ANALYZER_SUMMARY.md)** - Implementation details
- **[TEST_PLAN.md](../TEST_PLAN.md)** - Detailed test specifications

## Contributing

Found an issue or want to improve a guide?

1. Check if issue exists in README.md
2. Try the Troubleshooting section in relevant guide
3. Consult Additional Resources above
4. Open an issue with details

## License

See [LICENSE](../LICENSE) file for details.

---

**Need help?** Start with the [Quick Test workflow](#workflow-1-quick-test-15-minutes) above, then refer to specific guides as needed.
