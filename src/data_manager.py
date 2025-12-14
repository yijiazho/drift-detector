"""
Data Manager for Drift Detection System

Provides unified, schema-validated data operations for all system components.
Handles reading and writing predictions, window metadata, and drift detection results.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile
import shutil

# Import schema validation
import sys
sys.path.append(str(Path(__file__).parent.parent / 'schemas'))
from schema_registry import get_registry, ValidationError


class DataManager:
    """
    Centralized data manager with schema validation.

    Provides type-safe read/write operations for all data formats in the system.
    """

    def __init__(self, validate: bool = True):
        """
        Initialize the data manager.

        Args:
            validate: If True, validates all data against schemas
        """
        self.validate = validate
        self.registry = get_registry() if validate else None

    # ==================== Prediction Operations ====================

    def append_prediction(self, log_file: Path, prediction: Dict[str, Any],
                         validate: Optional[bool] = None) -> None:
        """
        Append a prediction to a JSONL log file.

        Args:
            log_file: Path to the JSONL log file
            prediction: Prediction dictionary
            validate: Override instance validation setting

        Raises:
            ValidationError: If validation fails
        """
        should_validate = validate if validate is not None else self.validate

        if should_validate:
            self.registry.validate(prediction, 'prediction')

        # Append to JSONL file
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(json.dumps(prediction) + '\n')

    def read_predictions(self, log_file: Path,
                        validate: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Read predictions from a JSONL log file.

        Args:
            log_file: Path to the JSONL log file
            validate: Override instance validation setting

        Returns:
            List of prediction dictionaries

        Raises:
            FileNotFoundError: If log file doesn't exist
            ValidationError: If validation fails
        """
        if not log_file.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")

        predictions = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    predictions.append(json.loads(line))

        should_validate = validate if validate is not None else self.validate
        if should_validate:
            self.registry.validate_list(predictions, 'prediction')

        return predictions

    # ==================== Window Metadata Operations ====================

    def write_window_metadata(self, output_file: Path,
                             windows: List[Dict[str, Any]],
                             validate: Optional[bool] = None) -> None:
        """
        Write window metadata to a JSON file.

        Args:
            output_file: Path to the output JSON file
            windows: List of window metadata dictionaries
            validate: Override instance validation setting

        Raises:
            ValidationError: If validation fails
        """
        should_validate = validate if validate is not None else self.validate

        if should_validate:
            self.registry.validate_list(windows, 'window_metadata')

        # Atomic write: write to temp file, then rename
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                        dir=output_file.parent,
                                        suffix='.tmp') as tmp_file:
            json.dump(windows, tmp_file, indent=2)
            tmp_path = tmp_file.name

        shutil.move(tmp_path, output_file)

    def read_window_metadata(self, metadata_file: Path,
                            validate: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Read window metadata from a JSON file.

        Args:
            metadata_file: Path to the metadata JSON file
            validate: Override instance validation setting

        Returns:
            List of window metadata dictionaries

        Raises:
            FileNotFoundError: If metadata file doesn't exist
            ValidationError: If validation fails
        """
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        with open(metadata_file, 'r') as f:
            windows = json.load(f)

        should_validate = validate if validate is not None else self.validate
        if should_validate:
            self.registry.validate_list(windows, 'window_metadata')

        return windows

    # ==================== Drift Detection Operations ====================

    def write_drift_detections(self, output_file: Path,
                              detections: List[Dict[str, Any]],
                              validate: Optional[bool] = None) -> None:
        """
        Write drift detection results to a JSON file.

        Args:
            output_file: Path to the output JSON file
            detections: List of drift detection dictionaries
            validate: Override instance validation setting

        Raises:
            ValidationError: If validation fails
        """
        should_validate = validate if validate is not None else self.validate

        if should_validate:
            self.registry.validate_list(detections, 'drift_detection')

        # Atomic write: write to temp file, then rename
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                        dir=output_file.parent,
                                        suffix='.tmp') as tmp_file:
            json.dump(detections, tmp_file, indent=2)
            tmp_path = tmp_file.name

        shutil.move(tmp_path, output_file)

    def read_drift_detections(self, detection_file: Path,
                             validate: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Read drift detection results from a JSON file.

        Args:
            detection_file: Path to the detection JSON file
            validate: Override instance validation setting

        Returns:
            List of drift detection dictionaries

        Raises:
            FileNotFoundError: If detection file doesn't exist
            ValidationError: If validation fails
        """
        if not detection_file.exists():
            raise FileNotFoundError(f"Detection file not found: {detection_file}")

        with open(detection_file, 'r') as f:
            detections = json.load(f)

        should_validate = validate if validate is not None else self.validate
        if should_validate:
            self.registry.validate_list(detections, 'drift_detection')

        return detections

    # ==================== Configuration Operations ====================

    def read_config(self, config_file: Path,
                   validate: Optional[bool] = None) -> Dict[str, Any]:
        """
        Read configuration from a JSON file.

        Args:
            config_file: Path to the config JSON file
            validate: Override instance validation setting

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If validation fails
        """
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, 'r') as f:
            config = json.load(f)

        should_validate = validate if validate is not None else self.validate
        if should_validate:
            self.registry.validate(config, 'config')

        return config

    # ==================== Utility Methods ====================

    def get_prediction_log_path(self, date: Optional[datetime] = None,
                               logs_dir: Path = None) -> Path:
        """
        Get the standard path for a prediction log file.

        Args:
            date: Date for the log file (defaults to today)
            logs_dir: Directory for logs (defaults to ./logs)

        Returns:
            Path to the log file
        """
        if date is None:
            date = datetime.now()
        if logs_dir is None:
            logs_dir = Path(__file__).parent.parent / 'logs'

        filename = f"predictions_{date.strftime('%Y%m%d')}.jsonl"
        return logs_dir / filename

    def validate_existing_files(self, verbose: bool = True) -> Dict[str, bool]:
        """
        Validate all existing data files in standard locations.

        Args:
            verbose: If True, prints validation results

        Returns:
            Dictionary mapping file paths to validation status
        """
        base_dir = Path(__file__).parent.parent
        results = {}

        # Check prediction logs
        logs_dir = base_dir / 'logs'
        if logs_dir.exists():
            for log_file in logs_dir.glob('predictions_*.jsonl'):
                try:
                    self.registry.validate_file(log_file, 'prediction', is_jsonl=True)
                    results[str(log_file)] = True
                    if verbose:
                        print(f"✓ {log_file.name}")
                except Exception as e:
                    results[str(log_file)] = False
                    if verbose:
                        print(f"✗ {log_file.name}: {str(e)}")

        # Check window metadata
        metadata_file = base_dir / 'outputs' / 'metadata' / 'window_metadata.json'
        if metadata_file.exists():
            try:
                self.registry.validate_file(metadata_file, 'window_metadata')
                results[str(metadata_file)] = True
                if verbose:
                    print(f"✓ {metadata_file.name}")
            except Exception as e:
                results[str(metadata_file)] = False
                if verbose:
                    print(f"✗ {metadata_file.name}: {str(e)}")

        # Check drift detection results
        detection_file = base_dir / 'outputs' / 'detection' / 'drift_detection.json'
        if detection_file.exists():
            try:
                self.registry.validate_file(detection_file, 'drift_detection')
                results[str(detection_file)] = True
                if verbose:
                    print(f"✓ {detection_file.name}")
            except Exception as e:
                results[str(detection_file)] = False
                if verbose:
                    print(f"✗ {detection_file.name}: {str(e)}")

        # Check config files
        configs_dir = base_dir / 'configs'
        if configs_dir.exists():
            for config_file in configs_dir.glob('config_*.json'):
                try:
                    self.registry.validate_file(config_file, 'config')
                    results[str(config_file)] = True
                    if verbose:
                        print(f"✓ {config_file.name}")
                except Exception as e:
                    results[str(config_file)] = False
                    if verbose:
                        print(f"✗ {config_file.name}: {str(e)}")

        return results


if __name__ == "__main__":
    # Demo: validate existing data files
    print("=" * 60)
    print("Data Manager - Validating Existing Files")
    print("=" * 60)

    dm = DataManager(validate=True)
    results = dm.validate_existing_files(verbose=True)

    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(results.values())
    print(f"Summary: {passed}/{total} files passed validation")
    print("=" * 60)
