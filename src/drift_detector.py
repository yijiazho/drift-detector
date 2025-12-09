"""
Drift Detection Engine for Epic 3: Drift Detection Engine
Uses ADWIN algorithm to detect drift in prediction streams.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
from river.drift import ADWIN


class WindowedPredictions:
    """Container for a window of predictions."""

    def __init__(self, window_id: int, predictions: List[Dict], metadata: Optional[Dict] = None):
        self.window_id = window_id
        self.predictions = predictions
        self.metadata = metadata or {}

    @property
    def prediction_values(self) -> np.ndarray:
        """Extract prediction values as numpy array."""
        return np.array([p["prediction"] for p in self.predictions])

    @property
    def mean(self) -> float:
        """Calculate mean of predictions in window."""
        return float(self.prediction_values.mean())

    @property
    def std(self) -> float:
        """Calculate standard deviation of predictions in window."""
        return float(self.prediction_values.std())

    @property
    def count(self) -> int:
        """Number of predictions in window."""
        return len(self.predictions)

    @property
    def timestamp(self) -> str:
        """Get timestamp of the last prediction in window."""
        if self.predictions:
            return self.predictions[-1]["timestamp"]
        return datetime.utcnow().isoformat() + "Z"


class DriftDetector:
    """
    Drift detection engine using ADWIN algorithm.

    Processes predictions in windows and detects drift using River's ADWIN.
    """

    def __init__(self, window_size: int = 100, delta: float = 0.002):
        """
        Initialize drift detector.

        Args:
            window_size: Number of predictions per window
            delta: ADWIN sensitivity parameter (smaller = more sensitive)
        """
        self.window_size = window_size
        self.delta = delta
        self.adwin = ADWIN(delta=delta)

        # Statistics tracking
        self.baseline_mean = None
        self.windows = []
        self.detection_results = []

    def load_predictions(self, log_file: str) -> List[Dict]:
        """
        Load predictions from JSONL log file.

        Args:
            log_file: Path to predictions JSONL file

        Returns:
            List of prediction dictionaries
        """
        predictions = []
        with open(log_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    predictions.append(json.loads(line))
        return predictions

    def load_window_metadata(self, metadata_file: str) -> List[Dict]:
        """
        Load window metadata from JSON file.

        Args:
            metadata_file: Path to window metadata JSON

        Returns:
            List of window metadata dictionaries
        """
        with open(metadata_file, "r") as f:
            return json.load(f)

    def create_windows(self, predictions: List[Dict], metadata: Optional[List[Dict]] = None) -> List[WindowedPredictions]:
        """
        Group predictions into fixed-size windows.

        Args:
            predictions: List of prediction dictionaries
            metadata: Optional window metadata for validation

        Returns:
            List of WindowedPredictions objects
        """
        windows = []
        window_id = 0

        for i in range(0, len(predictions), self.window_size):
            window_predictions = predictions[i:i + self.window_size]

            # Match with metadata if available
            window_meta = None
            if metadata and window_id < len(metadata):
                window_meta = metadata[window_id]

            window = WindowedPredictions(window_id, window_predictions, window_meta)
            windows.append(window)
            window_id += 1

        return windows

    def detect_drift_in_window(self, window: WindowedPredictions) -> Dict:
        """
        Detect drift in a single window using ADWIN.

        Args:
            window: WindowedPredictions object

        Returns:
            Detection result dictionary
        """
        drift_detected_in_window = False

        # Feed each prediction to ADWIN
        for pred_value in window.prediction_values:
            self.adwin.update(pred_value)
            if self.adwin.drift_detected:
                drift_detected_in_window = True

        # Set baseline from first window
        if self.baseline_mean is None:
            self.baseline_mean = window.mean

        # Calculate drift statistic (absolute difference from baseline)
        drift_statistic = abs(window.mean - self.baseline_mean)

        # Create detection result
        result = {
            "window_id": window.window_id,
            "timestamp": window.timestamp,
            "drift_statistic": round(drift_statistic, 6),
            "drift_detected": drift_detected_in_window,
            "adwin_detected": drift_detected_in_window,
            "baseline_mean": round(self.baseline_mean, 6),
            "current_mean": round(window.mean, 6),
            "current_std": round(window.std, 6),
            "predictions_processed": window.count
        }

        # Add ground truth if available from metadata
        if window.metadata:
            result["ground_truth_drift"] = window.metadata.get("is_drift", None)

        return result

    def process_all_windows(self, predictions: List[Dict], metadata: Optional[List[Dict]] = None):
        """
        Process all predictions and detect drift.

        Args:
            predictions: List of prediction dictionaries
            metadata: Optional window metadata
        """
        print("=" * 70)
        print("Drift Detection Engine - Epic 3")
        print("=" * 70)
        print(f"Configuration:")
        print(f"  Window size: {self.window_size}")
        print(f"  ADWIN delta: {self.delta}")
        print(f"  Total predictions: {len(predictions)}")
        print()

        # Create windows
        self.windows = self.create_windows(predictions, metadata)
        print(f"Created {len(self.windows)} windows")
        print()

        # Process each window
        print("Processing windows...")
        for window in self.windows:
            result = self.detect_drift_in_window(window)
            self.detection_results.append(result)

            # Print result
            status = "DRIFT" if result["drift_detected"] else "STABLE"
            gt_status = ""
            if "ground_truth_drift" in result:
                gt = "DRIFT" if result["ground_truth_drift"] else "STABLE"
                match = "✓" if (result["drift_detected"] == result["ground_truth_drift"]) else "✗"
                gt_status = f" | Ground truth: {gt} {match}"

            print(f"  Window {result['window_id']:2d}: {status:6s} | "
                  f"stat={result['drift_statistic']:.4f} | "
                  f"mean={result['current_mean']:.4f}{gt_status}")

        print()

    def save_results(self, output_path: str = "data/drift_detection.json"):
        """
        Save drift detection results to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        Path(output_path).parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(self.detection_results, f, indent=2)

        print(f"✓ Drift detection results saved to {output_path}")
        print(f"  Total windows analyzed: {len(self.detection_results)}")

    def print_summary(self):
        """Print summary statistics."""
        if not self.detection_results:
            print("No results to summarize")
            return

        detected_count = sum(1 for r in self.detection_results if r["drift_detected"])
        total_count = len(self.detection_results)

        print("=" * 70)
        print("Detection Summary")
        print("=" * 70)
        print(f"Total windows: {total_count}")
        print(f"Drift detected: {detected_count}")
        print(f"Stable: {total_count - detected_count}")
        print(f"Detection rate: {100 * detected_count / total_count:.1f}%")
        print()

        # If ground truth available, calculate accuracy
        gt_results = [r for r in self.detection_results if "ground_truth_drift" in r]
        if gt_results:
            correct = sum(1 for r in gt_results if r["drift_detected"] == r["ground_truth_drift"])
            accuracy = 100 * correct / len(gt_results)
            print(f"Ground Truth Comparison:")
            print(f"  Accuracy: {accuracy:.1f}% ({correct}/{len(gt_results)})")

            # True positives, false positives, etc.
            tp = sum(1 for r in gt_results if r["drift_detected"] and r["ground_truth_drift"])
            fp = sum(1 for r in gt_results if r["drift_detected"] and not r["ground_truth_drift"])
            tn = sum(1 for r in gt_results if not r["drift_detected"] and not r["ground_truth_drift"])
            fn = sum(1 for r in gt_results if not r["drift_detected"] and r["ground_truth_drift"])

            print(f"  True Positives:  {tp}")
            print(f"  False Positives: {fp}")
            print(f"  True Negatives:  {tn}")
            print(f"  False Negatives: {fn}")

            if tp + fp > 0:
                precision = tp / (tp + fp)
                print(f"  Precision: {precision:.2f}")
            if tp + fn > 0:
                recall = tp / (tp + fn)
                print(f"  Recall: {recall:.2f}")


def main():
    """Main entry point for drift detection."""
    import argparse

    parser = argparse.ArgumentParser(description="Detect drift in prediction logs")
    parser.add_argument(
        "--log-file",
        type=str,
        default="logs/predictions_20251207.jsonl",
        help="Path to predictions log file"
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default="data/window_metadata.json",
        help="Path to window metadata file (optional)"
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=100,
        help="Window size for drift detection"
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=0.002,
        help="ADWIN delta parameter (smaller = more sensitive)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/drift_detection.json",
        help="Output file for detection results"
    )

    args = parser.parse_args()

    # Initialize detector
    detector = DriftDetector(window_size=args.window_size, delta=args.delta)

    # Load data
    predictions = detector.load_predictions(args.log_file)

    # Load metadata if available
    metadata = None
    try:
        metadata = detector.load_window_metadata(args.metadata)
    except FileNotFoundError:
        print(f"Note: Window metadata not found at {args.metadata}")
        print("Proceeding without ground truth labels\n")

    # Process windows and detect drift
    detector.process_all_windows(predictions, metadata)

    # Save results
    detector.save_results(args.output)

    # Print summary
    detector.print_summary()


if __name__ == "__main__":
    main()
