"""
Quick test script for real-time drift analyzer.
Tests the analyzer with simulated log file updates.
"""
import json
import time
import threading
from pathlib import Path
from datetime import datetime

# Test log file
test_log = Path("logs/test_realtime.jsonl")

def write_predictions():
    """Simulate writing predictions to log file."""
    print("Starting prediction writer...")
    time.sleep(2)  # Give analyzer time to start

    # Write baseline predictions (no drift)
    print("\n[Writer] Writing baseline predictions (mean=0.05)...")
    for i in range(20):
        prediction = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input_features": {
                "feature1": 5.0,
                "feature2": 2.0,
                "feature3": 1.0
            },
            "prediction": 0.05 + (i % 10) * 0.001,  # Small variance
            "model_version": "v1.0",
            "drift_phase": 1
        }
        with open(test_log, 'a') as f:
            f.write(json.dumps(prediction) + '\n')
        time.sleep(0.1)

    print("\n[Writer] Pausing before drift...")
    time.sleep(2)

    # Write drifted predictions (drift!)
    print("\n[Writer] Writing drifted predictions (mean=0.5)...")
    for i in range(20):
        prediction = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input_features": {
                "feature1": 8.0,
                "feature2": 3.0,
                "feature3": 2.0
            },
            "prediction": 0.5 + (i % 10) * 0.001,  # Drifted!
            "model_version": "v1.0",
            "drift_phase": 2
        }
        with open(test_log, 'a') as f:
            f.write(json.dumps(prediction) + '\n')
        time.sleep(0.1)

    print("\n[Writer] Done writing predictions!")

if __name__ == "__main__":
    # Clean up old test file
    if test_log.exists():
        test_log.unlink()

    print("=" * 70)
    print("Real-Time Drift Analyzer Test")
    print("=" * 70)
    print("\nThis test will:")
    print("1. Start writing predictions to a test log file")
    print("2. Write 20 baseline predictions (mean ~0.05)")
    print("3. Write 20 drifted predictions (mean ~0.5)")
    print("4. You should see drift detection in the analyzer output")
    print("\nTo run the test:")
    print("  1. Run this script in one terminal: python test_realtime.py")
    print("  2. In another terminal, run:")
    print("     python realtime_drift_analyzer.py --log-file logs/test_realtime.jsonl --window-size 10")
    print("\n" + "=" * 70)

    input("\nPress ENTER to start writing predictions...")

    # Start writer thread
    writer_thread = threading.Thread(target=write_predictions, daemon=True)
    writer_thread.start()

    # Wait for writer to finish
    writer_thread.join()

    print("\n" + "=" * 70)
    print("Test complete! Check the analyzer output for drift detection.")
    print("Press Ctrl+C in the analyzer terminal to see the summary.")
    print("=" * 70)
