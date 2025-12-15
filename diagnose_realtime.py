"""
Diagnostic tool for real-time drift analyzer issues.
"""
import json
from pathlib import Path
from datetime import datetime

def diagnose():
    """Diagnose common real-time analyzer issues."""
    print("=" * 70)
    print("Real-Time Drift Analyzer Diagnostics")
    print("=" * 70)
    print()

    # Check log file
    today = datetime.now().strftime("%Y%m%d")
    log_file = Path(f"logs/predictions_{today}.jsonl")

    print(f"1. Checking log file: {log_file}")
    if not log_file.exists():
        print(f"   ❌ Log file does not exist!")
        print(f"   Solution: Start model service and run simulation")
        return

    print(f"   ✅ Log file exists")

    # Count predictions
    try:
        with open(log_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            prediction_count = len(lines)

        print(f"   ✅ Total predictions in file: {prediction_count}")

        if prediction_count == 0:
            print(f"   ⚠️  File is empty - no predictions to process")
            return

        # Check first prediction
        first_pred = json.loads(lines[0])
        print(f"   ✅ First prediction timestamp: {first_pred['timestamp']}")

        # Check last prediction
        last_pred = json.loads(lines[-1])
        print(f"   ✅ Last prediction timestamp: {last_pred['timestamp']}")

        # Calculate window coverage
        windows = prediction_count // 100
        print(f"   ✅ Enough for {windows} windows (100 predictions each)")

        if windows == 0:
            print(f"   ⚠️  Need at least 100 predictions for one window")
            print(f"   Current: {prediction_count} predictions")
            print(f"   Need: {100 - prediction_count} more predictions")

    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return

    print()
    print("2. File Monitoring Setup")
    print(f"   Log file path: {log_file.absolute()}")
    print(f"   File size: {log_file.stat().st_size} bytes")
    print(f"   Last modified: {datetime.fromtimestamp(log_file.stat().st_mtime)}")

    print()
    print("3. Common Issues & Solutions")
    print()

    print("   Issue: Analyzer shows 0 predictions processed")
    print("   Cause: Analyzer started BEFORE simulation, only reads NEW lines")
    print("   Solution:")
    print("      Option 1: Restart analyzer AFTER simulation starts")
    print("      Option 2: Use --from-beginning flag (if implemented)")
    print("      Option 3: Delete log file and restart both")
    print()

    print("   Issue: Not enough predictions for a window")
    print(f"   Current: {prediction_count} predictions")
    if prediction_count < 100:
        print(f"   Need: Run simulation to generate at least 100 predictions")
    print()

    print("   Issue: Watchdog not detecting file changes")
    print("   Solution:")
    print("      - On macOS: Ensure FSEvents is working")
    print("      - Try: Kill and restart analyzer")
    print("      - Check: ls -l logs/ shows file is being updated")
    print()

    print("4. Recommended Test Procedure")
    print()
    print("   Step 1: Clean start")
    print(f"      rm {log_file}")
    print()
    print("   Step 2: Start analyzer FIRST")
    print(f"      python realtime_drift_analyzer.py --auto --window-size 10")
    print()
    print("   Step 3: Start simulation SECOND (in new terminal)")
    print(f"      python src/drift_simulator.py --config configs/config_simple.json")
    print()
    print("   You should see predictions being processed in real-time!")

    print()
    print("=" * 70)

if __name__ == "__main__":
    diagnose()
