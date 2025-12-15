# Guide: Creating the Model

## Overview

This guide covers creating the pre-fitted logistic regression model used by the drift detection system.

## Prerequisites

- Python 3.9+
- Virtual environment activated
- Dependencies installed: `pip install -r requirements.txt`

## Quick Start

```bash
python create_model.py
```

## What Happens

The script creates two files in the `models/` directory:

1. **model_v1.0.pkl** - The trained model
2. **model_metadata.pkl** - Model metadata

### Example Output

```
Pre-fitted model created successfully!
Model type: LogisticRegression
Number of features: 3
Feature names: feature1, feature2, feature3
Model saved to models/model_v1.0.pkl
Metadata saved to models/model_metadata.pkl

Test prediction with [3.5, 1.2, 0.8]: 0.0160
```

## Model Details

### Training Data

- **Dataset**: Iris dataset (first 3 features)
- **Target**: Binary classification (setosa vs others)
- **Algorithm**: Logistic Regression with default parameters
- **Random state**: 42 (for reproducibility)

### Model Specifications

```python
{
    "version": "v1.0",
    "model_type": "LogisticRegression",
    "n_features": 3,
    "feature_names": ["feature1", "feature2", "feature3"]
}
```

## File Locations

```
models/
├── model_v1.0.pkl          # Pickled scikit-learn model
└── model_metadata.pkl      # Model metadata dictionary
```

## Verification

Test that the model was created successfully:

```bash
# Check files exist
ls -lh models/

# Should show:
# model_v1.0.pkl (file size ~1-2KB)
# model_metadata.pkl (file size ~200 bytes)
```

## Using a Custom Model

### Option 1: Replace the Model

If you want to use your own model:

1. Train your model (must have 3 features)
2. Save as `models/model_v1.0.pkl`
3. Update `models/model_metadata.pkl` with correct feature names

### Option 2: Modify create_model.py

Edit `create_model.py` to use your own training data:

```python
# Replace these lines:
X = iris.data[:, :3]  # Use first 3 features
y = (iris.target > 0).astype(int)  # Binary classification

# With your own data:
X = your_training_features  # Shape: (n_samples, 3)
y = your_training_labels    # Shape: (n_samples,)
```

### Requirements for Custom Models

Your model must:
- Accept exactly 3 features as input
- Have a `predict_proba()` method
- Return probabilities for binary classification
- Be serializable with pickle

## Troubleshooting

### Error: "No module named 'sklearn'"

**Solution**: Install scikit-learn
```bash
pip install scikit-learn==1.3.2
```

### Error: "models directory not found"

**Solution**: Create the directory
```bash
mkdir -p models
python create_model.py
```

### Warning: Model file already exists

This is normal. The script will overwrite the existing model.

## Next Steps

After creating the model:

1. ✅ Model created → Start model service
   ```bash
   python src/model_service.py
   ```

2. ✅ Service running → Test predictions
   ```bash
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"features": {"feature1": 3.5, "feature2": 1.2, "feature3": 0.8}}'
   ```

3. ✅ Predictions working → Run drift simulation
   ```bash
   python src/drift_simulator.py --config configs/config_simple.json
   ```

## Related Guides

- [Starting the Model Service](02_model_service.md)
- [Making Predictions](03_predictions.md)
- [Running Drift Simulation](04_drift_simulation.md)

## Additional Resources

- **create_model.py**: Source code for model creation
- **README.md**: Project overview
- **requirements.txt**: All dependencies
