"""
Schema Registry for Drift Detection System

Provides JSON Schema validation for all data formats in the system.
Supports versioned schemas with backward compatibility.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError, Draft7Validator


class SchemaRegistry:
    """Central registry for JSON schemas with validation utilities."""

    def __init__(self, schema_dir: Optional[Path] = None):
        """
        Initialize the schema registry.

        Args:
            schema_dir: Directory containing schema files. If None, uses default location.
        """
        if schema_dir is None:
            # Default to schemas/ directory relative to this file
            self.schema_dir = Path(__file__).parent
        else:
            self.schema_dir = Path(schema_dir)

        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._load_schemas()

    def _load_schemas(self):
        """Load all schema files from the schema directory."""
        schema_files = {
            'prediction': 'prediction_v1.json',
            'window_metadata': 'window_metadata_v1.json',
            'drift_detection': 'drift_detection_v1.json',
            'config': 'config_v1.json'
        }

        for schema_name, filename in schema_files.items():
            schema_path = self.schema_dir / filename
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    self._schemas[schema_name] = json.load(f)
            else:
                print(f"Warning: Schema file not found: {schema_path}")

    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Get a schema by name.

        Args:
            schema_name: Name of the schema (e.g., 'prediction', 'window_metadata')

        Returns:
            The JSON schema dictionary

        Raises:
            KeyError: If schema not found
        """
        if schema_name not in self._schemas:
            raise KeyError(f"Schema '{schema_name}' not found. Available: {list(self._schemas.keys())}")
        return self._schemas[schema_name]

    def validate(self, data: Any, schema_name: str, raise_error: bool = True) -> bool:
        """
        Validate data against a schema.

        Args:
            data: Data to validate (dict or list of dicts)
            schema_name: Name of the schema to validate against
            raise_error: If True, raises ValidationError on failure. If False, returns False.

        Returns:
            True if validation passes, False if it fails (when raise_error=False)

        Raises:
            ValidationError: If validation fails and raise_error=True
            KeyError: If schema not found
        """
        schema = self.get_schema(schema_name)

        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            if raise_error:
                raise ValidationError(
                    f"Validation failed for schema '{schema_name}': {e.message}\n"
                    f"Path: {' -> '.join(str(p) for p in e.path)}"
                ) from e
            return False

    def validate_list(self, data_list: List[Dict[str, Any]], schema_name: str,
                     raise_error: bool = True) -> bool:
        """
        Validate a list of data items against a schema.

        Args:
            data_list: List of data items to validate
            schema_name: Name of the schema to validate against
            raise_error: If True, raises ValidationError on failure

        Returns:
            True if all items pass validation

        Raises:
            ValidationError: If any item fails validation and raise_error=True
        """
        for i, item in enumerate(data_list):
            try:
                self.validate(item, schema_name, raise_error=True)
            except ValidationError as e:
                if raise_error:
                    raise ValidationError(
                        f"Validation failed for item {i} in list: {e.message}"
                    ) from e
                return False
        return True

    def validate_file(self, file_path: Path, schema_name: str,
                     is_jsonl: bool = False, raise_error: bool = True) -> bool:
        """
        Validate a JSON or JSONL file against a schema.

        Args:
            file_path: Path to the file to validate
            schema_name: Name of the schema to validate against
            is_jsonl: If True, treats file as JSONL (one JSON object per line)
            raise_error: If True, raises ValidationError on failure

        Returns:
            True if validation passes

        Raises:
            ValidationError: If validation fails and raise_error=True
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if is_jsonl:
            # Validate JSONL format (predictions log)
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():  # Skip empty lines
                        try:
                            data = json.loads(line)
                            self.validate(data, schema_name, raise_error=True)
                        except (json.JSONDecodeError, ValidationError) as e:
                            if raise_error:
                                raise ValidationError(
                                    f"Validation failed at line {line_num}: {str(e)}"
                                ) from e
                            return False
        else:
            # Validate regular JSON format
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Handle both single objects and arrays
            if isinstance(data, list):
                return self.validate_list(data, schema_name, raise_error)
            else:
                return self.validate(data, schema_name, raise_error)

        return True

    def get_validator(self, schema_name: str) -> Draft7Validator:
        """
        Get a Draft7Validator for a schema.

        Args:
            schema_name: Name of the schema

        Returns:
            A configured Draft7Validator instance
        """
        schema = self.get_schema(schema_name)
        return Draft7Validator(schema)

    def list_schemas(self) -> List[str]:
        """
        Get a list of all available schema names.

        Returns:
            List of schema names
        """
        return list(self._schemas.keys())


# Global schema registry instance
_registry: Optional[SchemaRegistry] = None


def get_registry() -> SchemaRegistry:
    """
    Get the global schema registry instance (singleton pattern).

    Returns:
        The global SchemaRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = SchemaRegistry()
    return _registry


def validate_data(data: Any, schema_name: str, raise_error: bool = True) -> bool:
    """
    Convenience function to validate data using the global registry.

    Args:
        data: Data to validate
        schema_name: Name of the schema
        raise_error: If True, raises ValidationError on failure

    Returns:
        True if validation passes
    """
    return get_registry().validate(data, schema_name, raise_error)


def validate_file(file_path: Path, schema_name: str,
                 is_jsonl: bool = False, raise_error: bool = True) -> bool:
    """
    Convenience function to validate a file using the global registry.

    Args:
        file_path: Path to the file
        schema_name: Name of the schema
        is_jsonl: If True, treats file as JSONL format
        raise_error: If True, raises ValidationError on failure

    Returns:
        True if validation passes
    """
    return get_registry().validate_file(Path(file_path), schema_name, is_jsonl, raise_error)


if __name__ == "__main__":
    # Simple test/demo
    registry = SchemaRegistry()
    print("Available schemas:", registry.list_schemas())

    # Example: validate a prediction
    sample_prediction = {
        "timestamp": "2025-12-10T06:11:05.049989Z",
        "input_features": {
            "feature1": 5.17,
            "feature2": 1.92,
            "feature3": 1.19
        },
        "prediction": 0.049,
        "model_version": "v1.0",
        "drift_phase": 1
    }

    try:
        registry.validate(sample_prediction, 'prediction')
        print("✓ Sample prediction is valid")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
