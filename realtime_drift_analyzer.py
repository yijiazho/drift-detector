"""
Real-Time Drift Analyzer using File Tailing
Monitors prediction log files and performs live drift detection.
"""
import json
import time
import os
import signal
import sys
from pathlib import Path
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional, Deque
from dataclasses import dataclass, asdict

import numpy as np
from river.drift import ADWIN
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


@dataclass
class DriftAlert:
    """Container for drift detection alerts."""
    window_id: int
    timestamp: str
    drift_detected: bool
    drift_statistic: float
    baseline_mean: float
    current_mean: float
    current_std: float
    predictions_in_window: int
    alert_message: str


class PredictionWindow:
    """Manages a sliding window of predictions."""

    def __init__(self, window_size: int):
        """
        Initialize prediction window.

        Args:
            window_size: Maximum number of predictions in window
        """
        self.window_size = window_size
        self.predictions: Deque[Dict] = deque(maxlen=window_size)
        self.window_id = 0

    def add_prediction(self, prediction: Dict) -> bool:
        """
        Add a prediction to the window.

        Args:
            prediction: Prediction dictionary

        Returns:
            True if window is complete after addition
        """
        self.predictions.append(prediction)
        return len(self.predictions) >= self.window_size

    def get_prediction_values(self) -> np.ndarray:
        """Extract prediction values as numpy array."""
        return np.array([p["prediction"] for p in self.predictions])

    def get_mean(self) -> float:
        """Calculate mean of predictions in window."""
        values = self.get_prediction_values()
        return float(values.mean()) if len(values) > 0 else 0.0

    def get_std(self) -> float:
        """Calculate standard deviation of predictions in window."""
        values = self.get_prediction_values()
        return float(values.std()) if len(values) > 0 else 0.0

    def get_count(self) -> int:
        """Number of predictions in window."""
        return len(self.predictions)

    def get_timestamp(self) -> str:
        """Get timestamp of the last prediction."""
        if self.predictions:
            return self.predictions[-1]["timestamp"]
        return datetime.utcnow().isoformat() + "Z"

    def is_complete(self) -> bool:
        """Check if window has reached target size."""
        return len(self.predictions) >= self.window_size

    def clear(self):
        """Clear the window and increment window ID."""
        self.predictions.clear()
        self.window_id += 1


class RealtimeDriftDetector:
    """
    Real-time drift detector using ADWIN algorithm.
    Maintains sliding window and detects drift as predictions arrive.
    """

    def __init__(
        self,
        window_size: int = 100,
        delta: float = 0.002,
        alert_callback: Optional[callable] = None
    ):
        """
        Initialize real-time drift detector.

        Args:
            window_size: Number of predictions per window
            delta: ADWIN sensitivity parameter (smaller = more sensitive)
            alert_callback: Optional callback function for alerts
        """
        self.window_size = window_size
        self.delta = delta
        self.alert_callback = alert_callback

        # Initialize ADWIN and window
        self.adwin = ADWIN(delta=delta)
        self.window = PredictionWindow(window_size)

        # Statistics tracking
        self.baseline_mean: Optional[float] = None
        self.total_predictions = 0
        self.total_windows = 0
        self.drift_count = 0

        # Alert history
        self.alerts: List[DriftAlert] = []

    def process_prediction(self, prediction: Dict) -> Optional[DriftAlert]:
        """
        Process a single prediction and check for drift.

        Args:
            prediction: Prediction dictionary with 'prediction' key

        Returns:
            DriftAlert if drift detected, None otherwise
        """
        # Add to window
        window_complete = self.window.add_prediction(prediction)
        self.total_predictions += 1

        # Feed prediction value to ADWIN
        pred_value = prediction["prediction"]
        self.adwin.update(pred_value)

        # Check if window is complete
        if window_complete:
            alert = self._analyze_window()
            if alert:
                if self.alert_callback:
                    self.alert_callback(alert)
                self.alerts.append(alert)
                return alert

        return None

    def _analyze_window(self) -> Optional[DriftAlert]:
        """
        Analyze the current window for drift.

        Returns:
            DriftAlert if analysis triggered, None otherwise
        """
        # Set baseline from first window
        if self.baseline_mean is None:
            self.baseline_mean = self.window.get_mean()

        current_mean = self.window.get_mean()
        current_std = self.window.get_std()

        # Calculate drift statistic (absolute difference from baseline)
        drift_statistic = abs(current_mean - self.baseline_mean)

        # Check if ADWIN detected drift OR if mean differs significantly from baseline
        # ADWIN detects changes between consecutive windows, so we also check absolute drift
        adwin_drift = self.adwin.drift_detected

        # Also flag drift if mean differs from baseline by more than threshold
        # Use a threshold based on delta parameter: drift if difference > 10% of baseline
        threshold = self.delta * 50  # Scale delta to reasonable threshold (0.002 * 50 = 0.1 = 10%)
        baseline_drift = drift_statistic > threshold if self.baseline_mean > 0 else False

        drift_detected = adwin_drift or baseline_drift

        if drift_detected:
            self.drift_count += 1

        # Create alert (use total_windows as the ID since it hasn't been incremented yet)
        alert = DriftAlert(
            window_id=self.total_windows,
            timestamp=self.window.get_timestamp(),
            drift_detected=drift_detected,
            drift_statistic=round(drift_statistic, 6),
            baseline_mean=round(self.baseline_mean, 6),
            current_mean=round(current_mean, 6),
            current_std=round(current_std, 6),
            predictions_in_window=self.window.get_count(),
            alert_message=self._create_alert_message(
                drift_detected, drift_statistic, current_mean, adwin_drift, baseline_drift
            )
        )

        self.total_windows += 1

        # Clear window for next batch (increments window_id)
        self.window.clear()

        return alert

    def _create_alert_message(
        self,
        drift_detected: bool,
        drift_statistic: float,
        current_mean: float,
        adwin_drift: bool,
        baseline_drift: bool
    ) -> str:
        """Create human-readable alert message."""
        if drift_detected:
            change_pct = (drift_statistic / self.baseline_mean * 100) if self.baseline_mean != 0 else 0

            # Indicate which detector triggered
            detector_info = []
            if adwin_drift:
                detector_info.append("ADWIN")
            if baseline_drift:
                detector_info.append("Baseline")
            detector_str = f" [{', '.join(detector_info)}]" if detector_info else ""

            return (
                f"🚨 DRIFT DETECTED{detector_str}! Mean shifted from {self.baseline_mean:.4f} to "
                f"{current_mean:.4f} ({change_pct:+.1f}%)"
            )
        else:
            return f"✓ Stable - Mean: {current_mean:.4f}, Baseline: {self.baseline_mean:.4f}"

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        return {
            "total_predictions": self.total_predictions,
            "total_windows": self.total_windows,
            "drift_count": self.drift_count,
            "drift_rate": f"{100 * self.drift_count / self.total_windows:.1f}%" if self.total_windows > 0 else "0.0%",
            "baseline_mean": self.baseline_mean,
            "current_window_size": self.window.get_count()
        }


class PredictionLogMonitor(FileSystemEventHandler):
    """
    File system event handler for monitoring prediction log files.
    Tails the log file and processes new predictions in real-time.
    """

    def __init__(
        self,
        log_file: Path,
        drift_detector: RealtimeDriftDetector,
        verbose: bool = True,
        from_beginning: bool = False
    ):
        """
        Initialize log file monitor.

        Args:
            log_file: Path to the prediction log file
            drift_detector: RealtimeDriftDetector instance
            verbose: If True, print detailed output
            from_beginning: If True, process existing predictions from start
        """
        super().__init__()
        self.log_file = Path(log_file)
        self.drift_detector = drift_detector
        self.verbose = verbose

        # Track file position for tailing
        self.file_position = 0
        self.file_inode = None

        # Initialize position
        if self.log_file.exists():
            if from_beginning:
                # Start from beginning to process existing predictions
                self.file_position = 0
                if self.verbose:
                    print(f"📖 Processing existing predictions from beginning...")
                self._process_new_lines()  # Process existing content immediately
            else:
                # Normal tail behavior - only new predictions
                self.file_position = self.log_file.stat().st_size
            self.file_inode = self.log_file.stat().st_ino

    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification events."""
        if event.is_directory:
            return

        # Check if it's our target file
        if Path(event.src_path) == self.log_file:
            self._process_new_lines()

    def _process_new_lines(self):
        """Read and process new lines from the log file."""
        try:
            # Check if file was rotated (new inode)
            current_inode = self.log_file.stat().st_ino
            if self.file_inode is not None and current_inode != self.file_inode:
                if self.verbose:
                    print(f"⚠️  Log file rotated, resetting position")
                self.file_position = 0
                self.file_inode = current_inode

            with open(self.log_file, 'r') as f:
                # Seek to last position
                f.seek(self.file_position)

                # Read new lines
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            prediction = json.loads(line)
                            alert = self.drift_detector.process_prediction(prediction)

                            if alert:
                                self._print_alert(alert)
                        except json.JSONDecodeError as e:
                            if self.verbose:
                                print(f"⚠️  Invalid JSON: {e}")

                # Update position
                self.file_position = f.tell()

        except FileNotFoundError:
            if self.verbose:
                print(f"⚠️  Log file not found: {self.log_file}")
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Error processing log: {e}")

    def _print_alert(self, alert: DriftAlert):
        """Print alert to console."""
        print("\n" + "=" * 70)
        if alert.drift_detected:
            print(f"🚨 DRIFT ALERT - Window {alert.window_id}")
        else:
            print(f"✓ Window {alert.window_id} Complete")
        print("=" * 70)
        print(f"Timestamp:        {alert.timestamp}")
        print(f"Status:           {'DRIFT DETECTED' if alert.drift_detected else 'STABLE'}")
        print(f"Drift Statistic:  {alert.drift_statistic:.6f}")
        print(f"Baseline Mean:    {alert.baseline_mean:.6f}")
        print(f"Current Mean:     {alert.current_mean:.6f}")
        print(f"Current Std:      {alert.current_std:.6f}")
        print(f"Predictions:      {alert.predictions_in_window}")
        print(f"\n{alert.alert_message}")
        print("=" * 70 + "\n")


class RealtimeDriftAnalyzer:
    """
    Main real-time drift analyzer application.
    Orchestrates file monitoring and drift detection.
    """

    def __init__(
        self,
        log_file: Path,
        window_size: int = 100,
        delta: float = 0.002,
        verbose: bool = True,
        from_beginning: bool = False
    ):
        """
        Initialize real-time drift analyzer.

        Args:
            log_file: Path to prediction log file to monitor
            window_size: Number of predictions per window
            delta: ADWIN sensitivity parameter
            verbose: If True, print detailed output
            from_beginning: If True, process existing predictions from start
        """
        self.log_file = Path(log_file)
        self.window_size = window_size
        self.delta = delta
        self.verbose = verbose
        self.from_beginning = from_beginning

        # Initialize components
        self.drift_detector = RealtimeDriftDetector(
            window_size=window_size,
            delta=delta,
            alert_callback=None
        )

        self.monitor = PredictionLogMonitor(
            log_file=log_file,
            drift_detector=self.drift_detector,
            verbose=verbose,
            from_beginning=from_beginning
        )

        self.observer = Observer()
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n\n🛑 Shutting down gracefully...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Start monitoring the log file."""
        print("=" * 70)
        print("Real-Time Drift Analyzer")
        print("=" * 70)
        print(f"Monitoring:       {self.log_file}")
        print(f"Window size:      {self.window_size}")
        print(f"ADWIN delta:      {self.delta}")
        print(f"Started at:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print("\n⏳ Waiting for predictions...\n")

        # Setup file watching
        watch_dir = self.log_file.parent
        self.observer.schedule(self.monitor, str(watch_dir), recursive=False)
        self.observer.start()
        self.running = True

        # Keep running
        try:
            last_poll = time.time()
            poll_interval = 2  # Check file every 2 seconds as fallback

            while self.running:
                time.sleep(0.5)

                # Polling fallback - check file manually every poll_interval seconds
                # This is needed because watchdog may not reliably detect all file changes on macOS
                current_time = time.time()
                if current_time - last_poll >= poll_interval:
                    last_poll = current_time
                    # Manually trigger file check
                    self.monitor._process_new_lines()

                # Print periodic status (every 60 seconds)
                if self.verbose and int(time.time()) % 60 == 0:
                    self._print_status()

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop monitoring."""
        self.running = False
        self.observer.stop()
        self.observer.join()

        # Print final summary
        self._print_summary()

    def _print_status(self):
        """Print current status."""
        summary = self.drift_detector.get_summary()
        print("\n" + "-" * 70)
        print(f"📊 Status Update - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 70)
        print(f"Predictions processed: {summary['total_predictions']}")
        print(f"Windows analyzed:      {summary['total_windows']}")
        print(f"Drift detected:        {summary['drift_count']} ({summary['drift_rate']})")
        print(f"Current window:        {summary['current_window_size']}/{self.window_size} predictions")
        print("-" * 70 + "\n")

    def _print_summary(self):
        """Print final summary."""
        summary = self.drift_detector.get_summary()

        print("\n" + "=" * 70)
        print("FINAL SUMMARY")
        print("=" * 70)
        print(f"Total predictions:     {summary['total_predictions']}")
        print(f"Total windows:         {summary['total_windows']}")
        print(f"Drift detected:        {summary['drift_count']} windows")
        print(f"Detection rate:        {summary['drift_rate']}")
        if summary['baseline_mean'] is not None:
            print(f"Baseline mean:         {summary['baseline_mean']:.6f}")
        print("=" * 70)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Real-time drift detection using file tailing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor today's log file with defaults
  python realtime_drift_analyzer.py --log-file logs/predictions_20251214.jsonl

  # Custom window size and sensitivity
  python realtime_drift_analyzer.py --log-file logs/predictions_20251214.jsonl --window-size 50 --delta 0.001

  # Auto-detect today's log file
  python realtime_drift_analyzer.py --auto

  # Quiet mode (only show drift alerts)
  python realtime_drift_analyzer.py --log-file logs/predictions_20251214.jsonl --quiet

Press Ctrl+C to stop monitoring and see summary.
        """
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to prediction log file to monitor"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect today's log file"
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=100,
        help="Number of predictions per window (default: 100)"
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=0.002,
        help="ADWIN sensitivity - smaller=more sensitive (default: 0.002)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Quiet mode - only show drift alerts"
    )
    parser.add_argument(
        "--from-beginning",
        action="store_true",
        help="Process existing predictions from file start (default: only new predictions)"
    )

    args = parser.parse_args()

    # Determine log file
    if args.auto:
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = Path(f"logs/predictions_{date_str}.jsonl")
        print(f"Auto-detected log file: {log_file}")
    elif args.log_file:
        log_file = Path(args.log_file)
    else:
        print("Error: Either --log-file or --auto must be specified")
        parser.print_help()
        sys.exit(1)

    # Check if log file exists or can be created
    if not log_file.exists():
        print(f"\n⚠️  Warning: Log file does not exist yet: {log_file}")
        print("Waiting for file to be created...\n")

        # Create logs directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # Start analyzer
    analyzer = RealtimeDriftAnalyzer(
        log_file=log_file,
        window_size=args.window_size,
        delta=args.delta,
        verbose=not args.quiet,
        from_beginning=args.from_beginning
    )

    analyzer.start()


if __name__ == "__main__":
    main()
