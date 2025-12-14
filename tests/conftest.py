"""
Pytest configuration and shared fixtures for all tests.

This file contains fixtures that are automatically available to all test modules.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_prediction():
    """Sample prediction entry matching schema."""
    return {
        "timestamp": "2025-12-13T10:00:00Z",
        "input_features": {
            "feature1": 5.0,
            "feature2": 2.0,
            "feature3": 1.3
        },
        "prediction": 0.085,
        "model_version": "v1.0",
        "drift_phase": 1
    }


@pytest.fixture
def sample_predictions_list():
    """List of sample predictions for testing."""
    predictions = []
    for i in range(100):
        predictions.append({
            "timestamp": f"2025-12-13T10:{i:02d}:00Z",
            "input_features": {
                "feature1": 5.0 + (i * 0.01),
                "feature2": 2.0 + (i * 0.005),
                "feature3": 1.3 + (i * 0.003)
            },
            "prediction": 0.08 + (i * 0.001),
            "model_version": "v1.0",
            "drift_phase": 1 if i < 50 else 2
        })
    return predictions


@pytest.fixture
def sample_window_metadata():
    """Sample window metadata entry."""
    return {
        "window_id": 0,
        "start_timestamp": "2025-12-13T10:00:00Z",
        "end_timestamp": "2025-12-13T10:05:00Z",
        "is_drift": False,
        "is_simulated": True,
        "number_of_predictions": 100
    }


@pytest.fixture
def sample_drift_detection():
    """Sample drift detection result."""
    return {
        "window_id": 0,
        "timestamp": "2025-12-13T10:05:00Z",
        "drift_statistic": 0.0,
        "drift_detected": False,
        "adwin_detected": False,
        "baseline_mean": 0.085,
        "current_mean": 0.085,
        "current_std": 0.082,
        "predictions_processed": 100,
        "ground_truth_drift": False
    }


@pytest.fixture
def sample_config():
    """Sample configuration for drift simulation."""
    return {
        "simulation": {
            "request_rate": 10,
            "total_requests": 100,
            "window_size": 50
        },
        "drift_phases": [
            {
                "phase_id": 1,
                "name": "baseline",
                "num_requests": 50,
                "is_drift": False,
                "drift_type": "none",
                "distribution": {
                    "feature1": {"mean": 5.0, "std": 1.0},
                    "feature2": {"mean": 2.0, "std": 0.5},
                    "feature3": {"mean": 1.3, "std": 0.3}
                }
            },
            {
                "phase_id": 2,
                "name": "drift",
                "num_requests": 50,
                "is_drift": True,
                "drift_type": "abrupt",
                "distribution": {
                    "feature1": {"mean": 8.0, "std": 1.5},
                    "feature2": {"mean": 3.0, "std": 0.8},
                    "feature3": {"mean": 2.2, "std": 0.5}
                }
            }
        ]
    }


@pytest.fixture
def sample_prediction_log_file(temp_dir, sample_predictions_list):
    """Create a sample JSONL prediction log file."""
    log_file = temp_dir / "predictions_test.jsonl"
    with open(log_file, 'w') as f:
        for pred in sample_predictions_list:
            f.write(json.dumps(pred) + '\n')
    return log_file


@pytest.fixture
def sample_config_file(temp_dir, sample_config):
    """Create a sample config JSON file."""
    config_file = temp_dir / "config_test.json"
    with open(config_file, 'w') as f:
        json.dump(sample_config, f, indent=2)
    return config_file


@pytest.fixture
def invalid_prediction():
    """Invalid prediction missing required fields."""
    return {
        "timestamp": "2025-12-13T10:00:00Z",
        "input_features": {
            "feature1": 5.0,
            "feature2": 2.0
            # Missing feature3
        },
        "prediction": 0.085,
        "model_version": "v1.0"
    }


@pytest.fixture
def malformed_json_file(temp_dir):
    """Create a file with malformed JSON."""
    bad_file = temp_dir / "malformed.jsonl"
    with open(bad_file, 'w') as f:
        f.write('{"valid": "json"}\n')
        f.write('{invalid json without closing brace\n')
        f.write('{"another": "valid"}\n')
    return bad_file


# Project root fixture for file path resolution
@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


# Model paths fixtures
@pytest.fixture
def model_path(project_root):
    """Path to the model file."""
    return project_root / "models" / "model_v1.0.pkl"


@pytest.fixture
def metadata_path(project_root):
    """Path to the metadata file."""
    return project_root / "models" / "model_metadata.pkl"
