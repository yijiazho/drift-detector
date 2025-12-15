"""
Test script for Epic 1: Local Model Service
Tests the /predict endpoint and verifies logging functionality.
"""
import requests
import json
import time
from pathlib import Path
import pytest


def _check_service_running():
    """Check if model service is running."""
    try:
        response = requests.get("http://localhost:8000/", timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


@pytest.mark.skipif(not _check_service_running(), reason="Model service not running on localhost:8000")
def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    response = requests.get("http://localhost:8000/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    assert response.status_code == 200


@pytest.mark.skipif(not _check_service_running(), reason="Model service not running on localhost:8000")
def test_predict_endpoint():
    """Test the /predict endpoint with sample data."""
    print("Testing /predict endpoint...")

    # Test case from task specification
    test_request = {
        "features": {
            "feature1": 3.5,
            "feature2": 1.2,
            "feature3": 0.8
        }
    }

    response = requests.post(
        "http://localhost:8000/predict",
        json=test_request
    )

    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    result = response.json()
    print(f"Response:")
    print(json.dumps(result, indent=2))
    print()

    # Verify response contains required fields
    assert "prediction" in result
    assert 0 <= result["prediction"] <= 1


@pytest.mark.skipif(not _check_service_running(), reason="Model service not running on localhost:8000")
def test_multiple_predictions():
    """Test multiple predictions to verify logging."""
    print("Testing multiple predictions...")

    test_cases = [
        {"feature1": 5.0, "feature2": 2.0, "feature3": 1.5},
        {"feature1": 4.5, "feature2": 1.8, "feature3": 1.2},
        {"feature1": 3.0, "feature2": 1.0, "feature3": 0.5},
    ]

    for i, features in enumerate(test_cases, 1):
        response = requests.post(
            "http://localhost:8000/predict",
            json={"features": features}
        )
        assert response.status_code == 200, f"Test {i}: FAILED with status {response.status_code}"
        result = response.json()
        print(f"  Test {i}: prediction={result['prediction']:.4f}")
        assert "prediction" in result
        assert 0 <= result["prediction"] <= 1

        time.sleep(0.1)  # Small delay between requests

    print()


def verify_logs():
    """Verify that predictions are being logged."""
    print("Verifying prediction logs...")

    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("  ✗ Logs directory not found")
        return False

    log_files = list(logs_dir.glob("predictions_*.jsonl"))
    if not log_files:
        print("  ✗ No log files found")
        return False

    # Read the latest log file
    latest_log = sorted(log_files)[-1]
    print(f"  ✓ Found log file: {latest_log}")

    with open(latest_log, "r") as f:
        lines = f.readlines()

    print(f"  ✓ Number of logged predictions: {len(lines)}")

    # Show a sample log entry
    if lines:
        sample = json.loads(lines[-1])
        print(f"  ✓ Sample log entry:")
        print(json.dumps(sample, indent=4))

    print()
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Epic 1 - Model Service Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Health Check", test_health_check),
        ("Predict Endpoint", test_predict_endpoint),
        ("Multiple Predictions", test_multiple_predictions),
        ("Prediction Logging", verify_logs)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}\n")
            results.append((test_name, False))

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)
    print()
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")


if __name__ == "__main__":
    run_all_tests()
