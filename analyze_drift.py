"""
Analyze drift in prediction logs.
Shows statistics per window to verify drift is detectable.
"""
import json
from pathlib import Path
from datetime import datetime
import numpy as np


def load_predictions(log_file):
    """Load predictions from JSONL file."""
    predictions = []
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                predictions.append(json.loads(line))
    return predictions


def load_window_metadata(metadata_file):
    """Load window metadata."""
    with open(metadata_file, "r") as f:
        return json.load(f)


def analyze_by_window(predictions, windows):
    """Analyze predictions grouped by window."""
    print("=" * 70)
    print("Drift Analysis by Window")
    print("=" * 70)
    print()

    # Group predictions by window based on timestamp
    for window in windows:
        window_id = window["window_id"]
        start_time = datetime.fromisoformat(window["start_timestamp"].replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(window["end_timestamp"].replace("Z", "+00:00"))

        # Get predictions in this window
        window_predictions = [
            p["prediction"] for p in predictions
            if start_time <= datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) <= end_time
        ]

        if window_predictions:
            preds = np.array(window_predictions)
            print(f"Window {window_id} (drift={window['is_drift']}):")
            print(f"  Count: {len(preds)}")
            print(f"  Mean:  {preds.mean():.4f}")
            print(f"  Std:   {preds.std():.4f}")
            print(f"  Min:   {preds.min():.4f}")
            print(f"  Max:   {preds.max():.4f}")
            print()


def analyze_by_phase(predictions):
    """Analyze predictions grouped by drift phase."""
    print("=" * 70)
    print("Drift Analysis by Phase")
    print("=" * 70)
    print()

    # Group by drift phase
    phases = {}
    for pred in predictions:
        phase = pred["drift_phase"]
        if phase not in phases:
            phases[phase] = []
        phases[phase].append(pred["prediction"])

    for phase_id in sorted(phases.keys()):
        preds = np.array(phases[phase_id])
        print(f"Phase {phase_id}:")
        print(f"  Count: {len(preds)}")
        print(f"  Mean:  {preds.mean():.4f}")
        print(f"  Std:   {preds.std():.4f}")
        print(f"  Min:   {preds.min():.4f}")
        print(f"  Max:   {preds.max():.4f}")
        print()


def main():
    """Main entry point."""
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser(
        description="Analyze drift statistics in prediction logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - will prompt for log file if not provided
  python analyze_drift.py --log-file logs/predictions_20251208.jsonl

  # Specify custom files
  python analyze_drift.py --log-file logs/predictions_20251208.jsonl --metadata outputs/metadata/window_metadata.json
        """
    )
    parser.add_argument(
        "--log-file",
        type=str,
        required=False,
        help="Path to predictions JSONL file (required - will prompt if not provided)"
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default="outputs/metadata/window_metadata.json",
        help="Path to window metadata JSON file (default: outputs/metadata/window_metadata.json)"
    )

    args = parser.parse_args()

    # Get log file path - prompt if not provided
    log_file = args.log_file
    if not log_file:
        print("\n" + "=" * 70)
        print("Drift Analysis - Log File Required")
        print("=" * 70)
        print("\nAvailable log files in logs/ directory:")

        # List available log files
        if os.path.exists("logs"):
            log_files = sorted([f for f in os.listdir("logs") if f.endswith(".jsonl")])
            if log_files:
                for i, f in enumerate(log_files, 1):
                    print(f"  {i}. {f}")
                print()
            else:
                print("  (no log files found)")
                print("\n✗ Please run drift simulation first to generate prediction logs.")
                sys.exit(1)
        else:
            print("  (logs directory not found)")
            print("\n✗ Please run drift simulation first to generate prediction logs.")
            sys.exit(1)

        # Prompt for log file
        log_file = input("\nEnter the log file name (or full path): ").strip()

        if not log_file:
            print("\n✗ Error: Log file is required.")
            sys.exit(1)

        # If user entered just a filename, prepend logs/
        if not log_file.startswith("logs/") and not os.path.exists(log_file):
            log_file = f"logs/{log_file}"

    # Load data
    try:
        predictions = load_predictions(log_file)
        windows = load_window_metadata(args.metadata)
    except FileNotFoundError as e:
        print(f"\n✗ Error: File not found - {e}")
        print(f"  Make sure to run drift simulation first.")
        sys.exit(1)

    print(f"\nLoaded {len(predictions)} predictions across {len(windows)} windows\n")

    # Analyze
    analyze_by_window(predictions, windows)
    analyze_by_phase(predictions)

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    all_preds = np.array([p["prediction"] for p in predictions])
    print(f"Overall statistics:")
    print(f"  Total predictions: {len(all_preds)}")
    print(f"  Mean: {all_preds.mean():.4f}")
    print(f"  Std:  {all_preds.std():.4f}")
    print(f"  Range: [{all_preds.min():.4f}, {all_preds.max():.4f}]")


if __name__ == "__main__":
    main()
