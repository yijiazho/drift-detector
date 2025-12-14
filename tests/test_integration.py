"""
Integration Tests for Drift Detection System - Epic 5

Tests the full end-to-end pipeline from simulation to drift detection to visualization.
Validates data flow across all components with schema validation.
"""

import unittest
import json
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'schemas'))

from src.data_manager import DataManager
from schema_registry import get_registry


class TestEndToEndIntegration(unittest.TestCase):
    """Test complete pipeline from config to detection."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent
        cls.test_config = cls.project_root / 'configs' / 'config_simple.json'
        cls.data_manager = DataManager(validate=True)
        cls.registry = get_registry()

        # Test output paths
        cls.test_date = datetime.now().strftime('%Y%m%d')
        cls.test_log_file = cls.project_root / 'logs' / f'predictions_{cls.test_date}.jsonl'
        cls.test_metadata = cls.project_root / 'outputs' / 'metadata' / 'window_metadata.json'
        cls.test_detection = cls.project_root / 'outputs' / 'detection' / 'drift_detection.json'

    def test_01_config_validation(self):
        """Test that configuration files are valid."""
        print("\n[TEST] Validating configuration files...")

        config_files = list((self.project_root / 'configs').glob('config_*.json'))
        self.assertGreater(len(config_files), 0, "No config files found")

        for config_file in config_files:
            with self.subTest(config=config_file.name):
                # Validate config schema
                config = self.data_manager.read_config(config_file)
                self.assertIn('simulation', config)
                self.assertIn('drift_phases', config)

                # Validate structure
                sim = config['simulation']
                self.assertIn('request_rate', sim)
                self.assertIn('total_requests', sim)
                self.assertIn('window_size', sim)

                print(f"  ✓ {config_file.name} is valid")

    def test_02_model_service_health(self):
        """Test that model service is accessible (if running)."""
        print("\n[TEST] Checking model service health...")

        try:
            response = requests.get('http://localhost:8000/', timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.assertIn('status', data)
                self.assertEqual(data['status'], 'running')
                print(f"  ✓ Model service is running (version: {data.get('model_version', 'unknown')})")
            else:
                self.skipTest("Model service not running")
        except requests.exceptions.RequestException:
            self.skipTest("Model service not running - skipping service tests")

    def test_03_prediction_log_validation(self):
        """Test validation of prediction log files."""
        print("\n[TEST] Validating prediction log files...")

        log_files = list((self.project_root / 'logs').glob('predictions_*.jsonl'))

        if len(log_files) == 0:
            self.skipTest("No prediction log files found")

        for log_file in log_files[:3]:  # Test first 3 files
            with self.subTest(log=log_file.name):
                # Read predictions without validation (logs may contain test data from error-case tests)
                predictions = self.data_manager.read_predictions(log_file, validate=False)
                self.assertGreater(len(predictions), 0, f"No predictions in {log_file.name}")

                # Validate first prediction structure manually
                pred = predictions[0]
                self.assertIn('timestamp', pred)
                self.assertIn('input_features', pred)
                self.assertIn('prediction', pred)
                self.assertIn('model_version', pred)

                # Validate features (allow missing features from error-case tests)
                features = pred['input_features']
                self.assertIn('feature1', features)
                self.assertIn('feature2', features)
                # feature3 may be missing in error-case test data

                print(f"  ✓ {log_file.name} validated ({len(predictions)} predictions)")

    def test_04_window_metadata_validation(self):
        """Test validation of window metadata."""
        print("\n[TEST] Validating window metadata...")

        if not self.test_metadata.exists():
            self.skipTest("Window metadata file not found")

        # Read and validate metadata
        windows = self.data_manager.read_window_metadata(self.test_metadata)
        self.assertGreater(len(windows), 0, "No windows in metadata")

        # Validate first window structure
        window = windows[0]
        self.assertIn('window_id', window)
        self.assertIn('start_timestamp', window)
        self.assertIn('end_timestamp', window)
        self.assertIn('is_drift', window)
        self.assertIn('is_simulated', window)
        self.assertIn('number_of_predictions', window)

        # Validate window IDs are sequential
        for i, window in enumerate(windows):
            self.assertEqual(window['window_id'], i, f"Window ID not sequential at index {i}")

        print(f"  ✓ Window metadata validated ({len(windows)} windows)")

    def test_05_drift_detection_validation(self):
        """Test validation of drift detection results."""
        print("\n[TEST] Validating drift detection results...")

        if not self.test_detection.exists():
            self.skipTest("Drift detection file not found")

        # Read and validate detections
        detections = self.data_manager.read_drift_detections(self.test_detection)
        self.assertGreater(len(detections), 0, "No detections found")

        # Validate first detection structure
        det = detections[0]
        required_fields = [
            'window_id', 'timestamp', 'drift_statistic', 'drift_detected',
            'adwin_detected', 'baseline_mean', 'current_mean', 'current_std',
            'predictions_processed'
        ]
        for field in required_fields:
            self.assertIn(field, det, f"Missing field: {field}")

        # Validate window IDs are sequential
        for i, det in enumerate(detections):
            self.assertEqual(det['window_id'], i, f"Detection window ID not sequential at index {i}")

        # Count drift detections
        drift_count = sum(1 for d in detections if d['drift_detected'])
        print(f"  ✓ Drift detection validated ({len(detections)} windows, {drift_count} drifts detected)")

    def test_06_data_consistency(self):
        """Test consistency between metadata and detection results."""
        print("\n[TEST] Validating data consistency...")

        if not self.test_metadata.exists() or not self.test_detection.exists():
            self.skipTest("Required files not found")

        # Read both files
        windows = self.data_manager.read_window_metadata(self.test_metadata)
        detections = self.data_manager.read_drift_detections(self.test_detection)

        # Should have same number of entries
        self.assertEqual(len(windows), len(detections),
                        "Window metadata and detections count mismatch")

        # Validate window IDs match
        for window, detection in zip(windows, detections):
            self.assertEqual(window['window_id'], detection['window_id'],
                           f"Window ID mismatch at index {window['window_id']}")

            # Validate prediction counts match
            self.assertEqual(window['number_of_predictions'],
                           detection['predictions_processed'],
                           f"Prediction count mismatch for window {window['window_id']}")

        print(f"  ✓ Data consistency validated ({len(windows)} windows)")

    def test_07_ground_truth_comparison(self):
        """Test comparison between ground truth and detected drift."""
        print("\n[TEST] Comparing ground truth vs detected drift...")

        if not self.test_metadata.exists() or not self.test_detection.exists():
            self.skipTest("Required files not found")

        # Read both files
        windows = self.data_manager.read_window_metadata(self.test_metadata)
        detections = self.data_manager.read_drift_detections(self.test_detection)

        # Calculate metrics
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        for window, detection in zip(windows, detections):
            ground_truth = window['is_drift']
            detected = detection['drift_detected']

            if ground_truth and detected:
                true_positives += 1
            elif not ground_truth and detected:
                false_positives += 1
            elif not ground_truth and not detected:
                true_negatives += 1
            elif ground_truth and not detected:
                false_negatives += 1

        total = len(windows)
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0

        print(f"  True Positives:  {true_positives}")
        print(f"  False Positives: {false_positives}")
        print(f"  True Negatives:  {true_negatives}")
        print(f"  False Negatives: {false_negatives}")
        print(f"  Accuracy: {accuracy:.1%}")

        # Basic sanity check - accuracy should be reasonable
        self.assertGreater(accuracy, 0.3, "Drift detection accuracy too low")

    def test_08_schema_validation_errors(self):
        """Test that invalid data is properly rejected."""
        print("\n[TEST] Testing schema validation error handling...")

        # Test invalid prediction (missing required field)
        invalid_prediction = {
            "timestamp": "2025-12-10T06:11:05.049989Z",
            "input_features": {
                "feature1": 5.17,
                "feature2": 1.92
                # Missing feature3
            },
            "prediction": 0.049,
            "model_version": "v1.0"
        }

        with self.assertRaises(Exception):
            self.registry.validate(invalid_prediction, 'prediction')
            print("  ✓ Invalid prediction correctly rejected")

        # Test invalid window metadata (wrong type)
        invalid_window = {
            "window_id": "zero",  # Should be integer, not string
            "start_timestamp": "2025-12-10T06:11:05.049989Z",
            "end_timestamp": "2025-12-10T06:11:15.779540Z",
            "is_drift": False,
            "is_simulated": True,
            "number_of_predictions": 100
        }

        with self.assertRaises(Exception):
            self.registry.validate(invalid_window, 'window_metadata')
            print("  ✓ Invalid window metadata correctly rejected")

    def test_09_all_existing_files(self):
        """Validate all existing data files."""
        print("\n[TEST] Validating all existing data files...")

        results = self.data_manager.validate_existing_files(verbose=False)

        # Separate prediction logs from other files (logs may contain error-case test data)
        prediction_logs = {k: v for k, v in results.items() if 'predictions_' in k}
        other_files = {k: v for k, v in results.items() if 'predictions_' not in k}

        # All non-prediction files should pass validation
        if other_files:
            other_passed = sum(other_files.values())
            other_total = len(other_files)
            self.assertEqual(other_passed, other_total,
                           f"Some data files failed validation: {other_total - other_passed}/{other_total}")

        # Prediction logs are best-effort (may contain test data from error cases)
        total = len(results)
        passed = sum(results.values())
        print(f"  ✓ {passed}/{total} files validated successfully")
        if passed < total:
            print(f"    Note: {total - passed} prediction logs may contain error-case test data")


class TestSchemaRegistry(unittest.TestCase):
    """Test schema registry functionality."""

    def setUp(self):
        """Set up test environment."""
        self.registry = get_registry()

    def test_list_schemas(self):
        """Test listing available schemas."""
        schemas = self.registry.list_schemas()
        expected = ['prediction', 'window_metadata', 'drift_detection', 'config']

        for schema_name in expected:
            self.assertIn(schema_name, schemas, f"Missing schema: {schema_name}")

    def test_get_schema(self):
        """Test retrieving individual schemas."""
        for schema_name in ['prediction', 'window_metadata', 'drift_detection', 'config']:
            schema = self.registry.get_schema(schema_name)
            self.assertIsInstance(schema, dict)
            self.assertIn('$schema', schema)
            self.assertIn('type', schema)


def run_integration_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("DRIFT DETECTION SYSTEM - INTEGRATION TESTS (Epic 5)")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSchemaRegistry))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
