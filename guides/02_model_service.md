# Guide: Model Service

## Overview

This guide covers starting and using the FastAPI model service for drift detection.

## Prerequisites

- ✅ Model created (`python create_model.py`)
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ Port 8000 available

## Quick Start

```bash
python src/model_service.py
```

The service will start on http://localhost:8000

## Expected Output

```
✓ Model loaded successfully from models/model_v1.0.pkl
✓ Metadata loaded successfully from models/model_metadata.pkl
  Model version: v1.0
  Model type: LogisticRegression
  Features: ['feature1', 'feature2', 'feature3']
✓ Logs directory ready at logs
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Service Endpoints

### 1. Health Check Endpoint

**GET /** - Check if service is running

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "running",
  "model_version": "v1.0",
  "service": "Drift Detection Model Service"
}
```

### 2. Prediction Endpoint

**POST /predict** - Get model prediction

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

## Prediction Logging

All predictions are automatically logged to:
```
logs/predictions_YYYYMMDD.jsonl
```

### Log Entry Format

```json
{
  "timestamp": "2025-12-14T20:45:32.123456Z",
  "input_features": {
    "feature1": 3.5,
    "feature2": 1.2,
    "feature3": 0.8
  },
  "prediction": 0.016,
  "model_version": "v1.0",
  "drift_phase": 1
}
```

### Viewing Logs

```bash
# View latest log file
tail -f logs/predictions_$(date +%Y%m%d).jsonl

# View all predictions
cat logs/predictions_*.jsonl | jq .
```

## Configuration

### Change Port

```python
# Edit src/model_service.py, line 161
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

Or run with uvicorn directly:
```bash
uvicorn src.model_service:app --host 0.0.0.0 --port 9000
```

### Change Host

To make service accessible from other machines:
```bash
uvicorn src.model_service:app --host 0.0.0.0 --port 8000
```

To restrict to localhost only:
```bash
uvicorn src.model_service:app --host 127.0.0.1 --port 8000
```

## Testing the Service

### Manual Testing

Use the provided test script:
```bash
python test_service.py
```

Expected output:
```
Test 1: Health Check
✓ Status: running
✓ Model version: v1.0

Test 2: Single Prediction
✓ Prediction received: 0.016
✓ Model version: v1.0

Test 3: Multiple Predictions
✓ 5 predictions made successfully

Test 4: Prediction Logging
✓ Predictions logged to: logs/predictions_20251214.jsonl

All tests passed!
```

### API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running in Production

### Using Uvicorn

For production deployments:

```bash
# With multiple workers
uvicorn src.model_service:app --host 0.0.0.0 --port 8000 --workers 4

# With auto-reload (development only)
uvicorn src.model_service:app --reload
```

### Using Gunicorn

For better production performance:

```bash
pip install gunicorn
gunicorn src.model_service:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### As a Background Service

#### Using screen (simple)
```bash
screen -S model-service
python src/model_service.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r model-service
```

#### Using systemd (production)

Create `/etc/systemd/system/drift-model.service`:

```ini
[Unit]
Description=Drift Detection Model Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/drift-detector
Environment="PATH=/path/to/drift-detector/venv/bin"
ExecStart=/path/to/drift-detector/venv/bin/python src/model_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl start drift-model
sudo systemctl enable drift-model  # Start on boot
```

## Monitoring

### Check Service Status

```bash
# Check if running
curl http://localhost:8000/ || echo "Service is down"

# Check logs
tail -f logs/predictions_*.jsonl
```

### Performance Monitoring

```bash
# Request count
wc -l logs/predictions_$(date +%Y%m%d).jsonl

# Average prediction value
cat logs/predictions_$(date +%Y%m%d).jsonl | jq -r '.prediction' | awk '{sum+=$1; count++} END {print sum/count}'
```

## Troubleshooting

### Error: "Model file not found"

**Solution**: Create the model first
```bash
python create_model.py
```

### Error: "Port 8000 already in use"

**Solution**: Either kill the existing process or use a different port
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn src.model_service:app --port 8001
```

### Error: "Import error: No module named 'fastapi'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Service starts but predictions fail

**Check:**
1. Model files exist in `models/` directory
2. Model has 3 features (feature1, feature2, feature3)
3. Request JSON format is correct

## Next Steps

After starting the service:

1. ✅ Service running → Make test predictions
   - See [Making Predictions Guide](03_predictions.md)

2. ✅ Predictions working → Run drift simulation
   - See [Drift Simulation Guide](04_drift_simulation.md)

3. ✅ Data generated → Detect drift
   - See [Batch Detection Guide](05_batch_detection.md)
   - See [Real-Time Detection Guide](06_realtime_detection.md)

## Related Guides

- [Creating the Model](01_creating_model.md)
- [Making Predictions](03_predictions.md)
- [Running Drift Simulation](04_drift_simulation.md)
- [Batch Drift Detection](05_batch_detection.md)
- [Real-Time Drift Detection](06_realtime_detection.md)

## Additional Resources

- **src/model_service.py**: Service source code
- **test_service.py**: Service test suite
- **API Docs**: http://localhost:8000/docs (when service is running)
