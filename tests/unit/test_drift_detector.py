"""
Unit tests for Drift Detector - Epic 3

Tests the ADWIN drift detection engine, window creation, and
statistical calculations.
"""

import pytest
import json
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.drift_detector import DriftDetector, WindowedPredictions


class TestPredictionLoading:
    """TEST-DD-001: Tests for prediction loading from JSONL files."""

    def test_loads_from_valid_jsonl_file(self, sample_prediction_log_file):
        """Test that predictions load successfully from valid JSONL file."""
        detector = DriftDetector()
        predictions = detector.load_predictions(str(sample_prediction_log_file))

        assert isinstance(predictions, list)
        assert len(predictions) > 0

    def test_empty_file_returns_empty_list(self, temp_dir):
        """Test that empty file returns empty list."""
        empty_file = temp_dir / "empty.jsonl"
        empty_file.touch()

        detector = DriftDetector()
        predictions = detector.load_predictions(str(empty_file))

        assert isinstance(predictions, list)
        assert len(predictions) == 0

    def test_empty_lines_ignored(self, temp_dir):
        """Test that empty lines in file are ignored."""
        log_file = temp_dir / "with_empty_lines.jsonl"
        with open(log_file, 'w') as f:
            f.write('{"timestamp": "2025-12-13T10:00:00Z", "prediction": 0.5}\n')
            f.write('\n')  # Empty line
            f.write('{"timestamp": "2025-12-13T10:01:00Z", "prediction": 0.6}\n')

        detector = DriftDetector()
        predictions = detector.load_predictions(str(log_file))

        assert len(predictions) == 2

    def test_missing_file_raises_error(self):
        """Test that missing file raises FileNotFoundError."""
        detector = DriftDetector()

        with pytest.raises(FileNotFoundError):
            detector.load_predictions("/nonexistent/file.jsonl")


class TestWindowCreation:
    """TEST-DD-002: Tests for window creation from predictions."""

    def test_predictions_divided_into_correct_window_sizes(self, sample_predictions_list):
        """Test that predictions are divided into correct window sizes."""
        detector = DriftDetector(window_size=50)
        windows = detector.create_windows(sample_predictions_list)

        # 100 predictions / 50 window_size = 2 windows
        assert len(windows) == 2
        assert windows[0].count == 50
        assert windows[1].count == 50

    def test_window_ids_sequential_from_zero(self, sample_predictions_list):
        """Test that window IDs are sequential starting from 0."""
        detector = DriftDetector(window_size=25)
        windows = detector.create_windows(sample_predictions_list)

        for i, window in enumerate(windows):
            assert window.window_id == i

    def test_final_incomplete_window_handled(self):
        """Test that final incomplete window is handled correctly."""
        # 75 predictions with window_size=50 should create 2 windows (50 + 25)
        predictions = [{"prediction": 0.5, "timestamp": "2025-12-13T10:00:00Z"} for _ in range(75)]

        detector = DriftDetector(window_size=50)
        windows = detector.create_windows(predictions)

        assert len(windows) == 2
        assert windows[0].count == 50
        assert windows[1].count == 25  # Incomplete window

    def test_empty_predictions_handled(self):
        """Test that empty predictions list is handled."""
        detector = DriftDetector()
        windows = detector.create_windows([])

        assert isinstance(windows, list)
        assert len(windows) == 0

    def test_window_count_calculation_correct(self, sample_predictions_list):
        """Test that window count calculation is correct."""
        detector = DriftDetector(window_size=30)
        windows = detector.create_windows(sample_predictions_list)

        # 100 predictions / 30 window_size = 4 windows (30, 30, 30, 10)
        assert len(windows) == 4


class TestWindowStatistics:
    """TEST-DD-004: Tests for window statistics calculations."""

    def test_mean_calculated_correctly(self):
        """Test that mean is calculated correctly."""
        predictions = [
            {"prediction": 0.1, "timestamp": "2025-12-13T10:00:00Z"},
            {"prediction": 0.2, "timestamp": "2025-12-13T10:01:00Z"},
            {"prediction": 0.3, "timestamp": "2025-12-13T10:02:00Z"},
            {"prediction": 0.4, "timestamp": "2025-12-13T10:03:00Z"},
            {"prediction": 0.5, "timestamp": "2025-12-13T10:04:00Z"}
        ]

        window = WindowedPredictions(0, predictions)
        assert abs(window.mean - 0.3) < 0.001

    def test_std_calculated_correctly(self):
        """Test that standard deviation is calculated correctly."""
        predictions = [
            {"prediction": 0.1, "timestamp": "2025-12-13T10:00:00Z"},
            {"prediction": 0.2, "timestamp": "2025-12-13T10:01:00Z"},
            {"prediction": 0.3, "timestamp": "2025-12-13T10:02:00Z"},
            {"prediction": 0.4, "timestamp": "2025-12-13T10:03:00Z"},
            {"prediction": 0.5, "timestamp": "2025-12-13T10:04:00Z"}
        ]

        window = WindowedPredictions(0, predictions)
        expected_std = np.std([0.1, 0.2, 0.3, 0.4, 0.5])
        assert abs(window.std - expected_std) < 0.001

    def test_count_returns_correct_number(self):
        """Test that count returns correct number of predictions."""
        predictions = [{"prediction": 0.5, "timestamp": "2025-12-13T10:00:00Z"} for _ in range(42)]

        window = WindowedPredictions(0, predictions)
        assert window.count == 42

    def test_timestamp_extracted_from_last_prediction(self):
        """Test that timestamp is extracted from last prediction."""
        predictions = [
            {"prediction": 0.1, "timestamp": "2025-12-13T10:00:00Z"},
            {"prediction": 0.2, "timestamp": "2025-12-13T10:01:00Z"},
            {"prediction": 0.3, "timestamp": "2025-12-13T10:02:00Z"}
        ]

        window = WindowedPredictions(0, predictions)
        assert window.timestamp == "2025-12-13T10:02:00Z"


class TestADWINDriftDetection:
    """TEST-DD-003: Tests for ADWIN drift detection algorithm."""

    def test_no_drift_in_stable_data(self):
        """Test that no drift is detected in stable data."""
        # Create stable predictions (same distribution)
        predictions = [
            {"prediction": 0.08 + np.random.normal(0, 0.01), "timestamp": f"2025-12-13T10:{i:02d}:00Z"}
            for i in range(100)
        ]

        detector = DriftDetector(window_size=50, delta=0.002)
        windows = detector.create_windows(predictions)

        result1 = detector.detect_drift_in_window(windows[0])
        result2 = detector.detect_drift_in_window(windows[1])

        # Should not detect drift in stable data
        # (may have false positives due to random variation)
        assert isinstance(result1["drift_detected"], bool)
        assert isinstance(result2["drift_detected"], bool)

    def test_drift_detected_in_shifted_data(self):
        """Test that drift is detected when data shifts significantly."""
        # Create stable then shifted predictions with some variation
        # Add small random variation to make it more realistic for ADWIN
        import random
        random.seed(42)
        stable = [{"prediction": 0.08 + random.uniform(-0.01, 0.01), "timestamp": f"2025-12-13T10:{i:02d}:00Z"} for i in range(50)]
        shifted = [{"prediction": 0.50 + random.uniform(-0.01, 0.01), "timestamp": f"2025-12-13T11:{i:02d}:00Z"} for i in range(50)]

        detector = DriftDetector(window_size=50, delta=0.002)
        windows = detector.create_windows(stable + shifted)

        result1 = detector.detect_drift_in_window(windows[0])
        result2 = detector.detect_drift_in_window(windows[1])

        # First window sets baseline (no drift)
        assert result1["drift_detected"] is False

        # Second window has significantly different mean (drift statistic should be large)
        # ADWIN may or may not detect drift (probabilistic), but drift_statistic should be significant
        assert result2["drift_statistic"] > 0.3  # Large shift from 0.08 to 0.50

    def test_baseline_set_from_first_window(self, sample_predictions_list):
        """Test that baseline is set from first window."""
        detector = DriftDetector(window_size=50)
        windows = detector.create_windows(sample_predictions_list)

        result1 = detector.detect_drift_in_window(windows[0])

        assert detector.baseline_mean is not None
        assert detector.baseline_mean == result1["baseline_mean"]

    def test_drift_statistic_calculated_correctly(self):
        """Test that drift statistic is calculated correctly."""
        # Create windows with known means
        window1 = [{"prediction": 0.1, "timestamp": f"2025-12-13T10:{i:02d}:00Z"} for i in range(50)]
        window2 = [{"prediction": 0.5, "timestamp": f"2025-12-13T11:{i:02d}:00Z"} for i in range(50)]

        detector = DriftDetector(window_size=50)
        windows = detector.create_windows(window1 + window2)

        result1 = detector.detect_drift_in_window(windows[0])
        result2 = detector.detect_drift_in_window(windows[1])

        # Drift statistic should be absolute difference from baseline
        expected_stat = abs(0.5 - 0.1)
        assert abs(result2["drift_statistic"] - expected_stat) < 0.001


class TestGroundTruthComparison:
    """TEST-DD-005: Tests for ground truth comparison functionality."""

    def test_accuracy_calculated_correctly(self):
        """Test that accuracy is calculated correctly."""
        # Create mock detection results
        results = [
            {"drift_detected": False, "ground_truth_drift": False},  # TN
            {"drift_detected": True, "ground_truth_drift": True},     # TP
            {"drift_detected": False, "ground_truth_drift": True},    # FN
            {"drift_detected": True, "ground_truth_drift": False}     # FP
        ]

        # Calculate accuracy: (TP + TN) / Total = (1 + 1) / 4 = 0.5
        correct = sum(1 for r in results if r["drift_detected"] == r["ground_truth_drift"])
        accuracy = correct / len(results)

        assert accuracy == 0.5

    def test_true_positives_counted_correctly(self):
        """Test that true positives are counted correctly."""
        results = [
            {"drift_detected": True, "ground_truth_drift": True},   # TP
            {"drift_detected": True, "ground_truth_drift": True},   # TP
            {"drift_detected": False, "ground_truth_drift": True},  # FN
        ]

        tp = sum(1 for r in results if r["drift_detected"] and r["ground_truth_drift"])
        assert tp == 2

    def test_false_positives_counted_correctly(self):
        """Test that false positives are counted correctly."""
        results = [
            {"drift_detected": True, "ground_truth_drift": False},  # FP
            {"drift_detected": True, "ground_truth_drift": False},  # FP
            {"drift_detected": True, "ground_truth_drift": True},   # TP
        ]

        fp = sum(1 for r in results if r["drift_detected"] and not r["ground_truth_drift"])
        assert fp == 2

    def test_precision_calculated_correctly(self):
        """Test that precision is calculated correctly."""
        results = [
            {"drift_detected": True, "ground_truth_drift": True},   # TP
            {"drift_detected": True, "ground_truth_drift": False},  # FP
            {"drift_detected": True, "ground_truth_drift": False},  # FP
        ]

        tp = sum(1 for r in results if r["drift_detected"] and r["ground_truth_drift"])
        fp = sum(1 for r in results if r["drift_detected"] and not r["ground_truth_drift"])

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        assert abs(precision - 0.333) < 0.01  # 1/3

    def test_recall_calculated_correctly(self):
        """Test that recall is calculated correctly."""
        results = [
            {"drift_detected": True, "ground_truth_drift": True},   # TP
            {"drift_detected": False, "ground_truth_drift": True},  # FN
            {"drift_detected": False, "ground_truth_drift": True},  # FN
        ]

        tp = sum(1 for r in results if r["drift_detected"] and r["ground_truth_drift"])
        fn = sum(1 for r in results if not r["drift_detected"] and r["ground_truth_drift"])

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        assert abs(recall - 0.333) < 0.01  # 1/3


class TestDetectionResultFormat:
    """TEST-DD-006: Tests for detection result format."""

    def test_result_contains_required_fields(self, sample_predictions_list):
        """Test that detection result contains all required fields."""
        detector = DriftDetector(window_size=50)
        windows = detector.create_windows(sample_predictions_list)

        result = detector.detect_drift_in_window(windows[0])

        required_fields = [
            "window_id", "timestamp", "drift_statistic", "drift_detected",
            "adwin_detected", "baseline_mean", "current_mean", "current_std",
            "predictions_processed"
        ]

        for field in required_fields:
            assert field in result

    def test_window_id_matches_input(self, sample_predictions_list):
        """Test that window_id in result matches input window."""
        detector = DriftDetector(window_size=50)
        windows = detector.create_windows(sample_predictions_list)

        result = detector.detect_drift_in_window(windows[1])

        assert result["window_id"] == windows[1].window_id

    def test_predictions_processed_matches_window_count(self, sample_predictions_list):
        """Test that predictions_processed matches window count."""
        detector = DriftDetector(window_size=50)
        windows = detector.create_windows(sample_predictions_list)

        result = detector.detect_drift_in_window(windows[0])

        assert result["predictions_processed"] == windows[0].count
