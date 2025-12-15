# Guide: Making Predictions

## Overview

This guide covers making predictions with the drift detection model service.

## Prerequisites

- ✅ Model created (`python create_model.py`)
- ✅ Service running (`python src/model_service.py`)
- ✅ Service accessible at http://localhost:8000

## Making a Single Prediction

### Using curl

```bash
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
  "timestamp": "2025-12-14T20:45:32.123456Z"
}
```

### Using Python (requests)

```python
import requests

response = requests.post(
    'http://localhost:8000/predict',
    json={
        'features': {
            'feature1': 3.5,
            'feature2': 1.2,
            'feature3': 0.8
        }
    }
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Model version: {result['model_version']}")
print(f"Timestamp: {result['timestamp']}")
```

### Using Python (httpx)

```python
import httpx

with httpx.Client() as client:
    response = client.post(
        'http://localhost:8000/predict',
        json={
            'features': {
                'feature1': 3.5,
                'feature2': 1.2,
                'feature3': 0.8
            }
        }
    )
    result = response.json()
    print(f"Prediction: {result['prediction']}")
```

## Making Multiple Predictions

### Batch Predictions (Python)

```python
import requests

features_list = [
    {'feature1': 3.5, 'feature2': 1.2, 'feature3': 0.8},
    {'feature1': 5.0, 'feature2': 2.0, 'feature3': 1.5},
    {'feature1': 6.2, 'feature2': 2.5, 'feature3': 1.8},
]

predictions = []
for features in features_list:
    response = requests.post(
        'http://localhost:8000/predict',
        json={'features': features}
    )
    predictions.append(response.json())

# Print results
for i, pred in enumerate(predictions, 1):
    print(f"Prediction {i}: {pred['prediction']:.4f}")
```

### Using a Loop (Bash)

```bash
# Make 10 predictions
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d "{
      \"features\": {
        \"feature1\": $((RANDOM % 10)),
        \"feature2\": $((RANDOM % 5)),
        \"feature3\": $((RANDOM % 3))
      }
    }" | jq .prediction
  sleep 0.1
done
```

## Understanding Predictions

### Input Features

The model requires exactly 3 features:

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| feature1 | float | Any | First input feature |
| feature2 | float | Any | Second input feature |
| feature3 | float | Any | Third input feature |

### Prediction Output

The prediction is a **probability** value between 0 and 1:

- **0.0** = Low probability of positive class
- **0.5** = Equal probability
- **1.0** = High probability of positive class

### Example Interpretations

```
Prediction: 0.016  → Very low probability (1.6%)
Prediction: 0.250  → Low probability (25%)
Prediction: 0.500  → Equal probability (50%)
Prediction: 0.750  → High probability (75%)
Prediction: 0.984  → Very high probability (98.4%)
```

## Viewing Logged Predictions

All predictions are automatically logged to JSONL files.

### View Today's Predictions

```bash
# View all predictions
cat logs/predictions_$(date +%Y%m%d).jsonl | jq .

# View just prediction values
cat logs/predictions_$(date +%Y%m%d).jsonl | jq -r '.prediction'

# Count predictions
wc -l logs/predictions_$(date +%Y%m%d).jsonl
```

### Follow Live Predictions

```bash
# Watch predictions as they arrive
tail -f logs/predictions_$(date +%Y%m%d).jsonl | jq .
```

### Filter Predictions

```bash
# High predictions only (> 0.5)
cat logs/predictions_$(date +%Y%m%d).jsonl | jq 'select(.prediction > 0.5)'

# Predictions in time range
cat logs/predictions_$(date +%Y%m%d).jsonl | \
  jq 'select(.timestamp > "2025-12-14T20:00:00Z")'

# Average prediction value
cat logs/predictions_$(date +%Y%m%d).jsonl | \
  jq -r '.prediction' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count}'
```

## Request Validation

### Valid Request

```json
{
  "features": {
    "feature1": 3.5,
    "feature2": 1.2,
    "feature3": 0.8
  }
}
```

### Invalid Requests

**Missing feature:**
```json
{
  "features": {
    "feature1": 3.5,
    "feature2": 1.2
    // Missing feature3
  }
}
```
**Error**: 422 Unprocessable Entity

**Wrong data type:**
```json
{
  "features": {
    "feature1": "not a number",
    "feature2": 1.2,
    "feature3": 0.8
  }
}
```
**Error**: 422 Unprocessable Entity

**Missing features object:**
```json
{
  "feature1": 3.5,
  "feature2": 1.2,
  "feature3": 0.8
}
```
**Error**: 422 Unprocessable Entity

## Error Handling

### Python Example with Error Handling

```python
import requests

def make_prediction(features):
    """Make a prediction with error handling."""
    try:
        response = requests.post(
            'http://localhost:8000/predict',
            json={'features': features},
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to model service")
        print("Is the service running? Try: python src/model_service.py")
        return None

    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response.text}")
        return None

# Usage
result = make_prediction({
    'feature1': 3.5,
    'feature2': 1.2,
    'feature3': 0.8
})

if result:
    print(f"Prediction: {result['prediction']}")
```

## Performance Considerations

### Response Time

Typical response times:
- **Single prediction**: 10-50ms
- **Network latency**: 1-5ms (localhost)
- **Total**: 11-55ms per prediction

### Throughput

The service can handle:
- **Sequential**: ~50-100 requests/second
- **Parallel (4 workers)**: ~200-400 requests/second

### Rate Limiting

No built-in rate limiting. For production:

```python
# Add rate limiting with slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/predict")
@limiter.limit("100/minute")
async def predict(request: PredictionRequest):
    # ... existing code
```

## Testing

### Quick Test Script

```bash
# test_predictions.sh
#!/bin/bash

echo "Testing predictions..."

# Test 1: Valid prediction
echo "Test 1: Valid prediction"
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"feature1": 3.5, "feature2": 1.2, "feature3": 0.8}}' \
  | jq .

# Test 2: Check logging
echo "Test 2: Check logging"
sleep 1
tail -n 1 logs/predictions_$(date +%Y%m%d).jsonl | jq .

# Test 3: Multiple predictions
echo "Test 3: Multiple predictions"
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d "{\"features\": {\"feature1\": $i, \"feature2\": $i, \"feature3\": $i}}" \
    | jq -r .prediction
done

echo "All tests completed!"
```

## Next Steps

After making predictions:

1. ✅ Predictions working → Run drift simulation
   - See [Drift Simulation Guide](04_drift_simulation.md)

2. ✅ Logs generated → Analyze drift
   - See [Batch Detection Guide](05_batch_detection.md)
   - See [Real-Time Detection Guide](06_realtime_detection.md)

3. ✅ Drift detected → Visualize results
   - See [Dashboard Guide](07_dashboard.md)

## Related Guides

- [Model Service Guide](02_model_service.md)
- [Drift Simulation Guide](04_drift_simulation.md)
- [Batch Drift Detection](05_batch_detection.md)
- [Real-Time Drift Detection](06_realtime_detection.md)

## Additional Resources

- **src/model_service.py**: Service implementation
- **API Docs**: http://localhost:8000/docs
- **test_service.py**: Automated tests
