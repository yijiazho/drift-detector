# Epic 5: Storage & Integration - Implementation Guide

## Overview

Epic 5 implements unified JSON storage schemas with validation and comprehensive end-to-end integration tests for the drift detection system.

## What Was Implemented

### Task 5.1: Define Unified JSON Storage Schema ✓

**Location:** `schemas/` directory

Created standardized JSON Schema definitions for all data formats:

1. **prediction_v1.json** - Individual prediction log entries
2. **window_metadata_v1.json** - Window metadata with drift labels
3. **drift_detection_v1.json** - Drift detection results per window
4. **config_v1.json** - Simulation configuration files

**Key Features:**
- JSON Schema Draft-07 format
- Required field validation
- Type checking (number, string, integer, boolean)
- Format validation (ISO 8601 timestamps)
- Range constraints (e.g., prediction between 0-1)
- Versioning support (v1 suffix for future evolution)

### Task 5.2: Implement End-to-End Integration Test ✓

**Location:** `tests/test_integration.py`

Comprehensive test suite covering:

1. **Configuration Validation** - All config files match schema
2. **Model Service Health** - Service is running and accessible
3. **Prediction Log Validation** - JSONL files are valid
4. **Window Metadata Validation** - Sequential window IDs, correct structure
5. **Drift Detection Validation** - Detection results match schema
6. **Data Consistency** - Window IDs align across files
7. **Ground Truth Comparison** - Calculate detection accuracy metrics
8. **Schema Error Handling** - Invalid data is properly rejected
9. **Existing Files Validation** - All current data passes validation

**Test Results:** 11/11 tests passing ✓

## New Components

### 1. Schema Registry (`schemas/schema_registry.py`)

Central registry for JSON schemas with validation utilities.

**Key Functions:**
```python
from schema_registry import get_registry, validate_data

# Get global registry instance
registry = get_registry()

# Validate data
registry.validate(data, 'prediction')  # Raises ValidationError if invalid

# Validate file
registry.validate_file(file_path, 'window_metadata')

# Validate JSONL file
registry.validate_file(log_file, 'prediction', is_jsonl=True)
```

**Features:**
- Singleton pattern for global access
- Automatic schema loading
- Detailed error messages with field paths
- Support for both single objects and arrays
- JSONL format support

### 2. Data Manager (`src/data_manager.py`)

Unified data operations with automatic schema validation.

**Key Functions:**
```python
from src.data_manager import DataManager

# Initialize with validation enabled
dm = DataManager(validate=True)

# Prediction operations
dm.append_prediction(log_file, prediction_dict)
predictions = dm.read_predictions(log_file)

# Window metadata operations
dm.write_window_metadata(output_file, windows_list)
windows = dm.read_window_metadata(metadata_file)

# Drift detection operations
dm.write_drift_detections(output_file, detections_list)
detections = dm.read_drift_detections(detection_file)

# Configuration operations
config = dm.read_config(config_file)

# Validate all existing files
results = dm.validate_existing_files(verbose=True)
```

**Features:**
- Schema validation on all read/write operations
- Atomic writes (temp file + rename)
- Flexible validation control (enable/disable per operation)
- Standard file path helpers
- Batch validation utilities

## Usage Examples

### Validating Existing Data

```bash
# Validate all existing files
python src/data_manager.py

# Output:
# ✓ predictions_20251210.jsonl
# ✓ window_metadata.json
# ✓ drift_detection.json
# ✓ config_simple.json
# Summary: 6/6 files passed validation
```

### Running Integration Tests

```bash
# Run all tests
python tests/test_integration.py

# Output:
# Ran 11 tests in 1.086s
# OK
# Successes: 11
# Failures: 0
```

### Using in Your Code

```python
from src.data_manager import DataManager
from pathlib import Path

# Initialize data manager
dm = DataManager(validate=True)

# Read configuration (with validation)
config = dm.read_config(Path('configs/config_simple.json'))

# Read predictions
predictions = dm.read_predictions(
    Path('logs/predictions_20251210.jsonl')
)

# Write window metadata (with validation)
windows = [
    {
        "window_id": 0,
        "start_timestamp": "2025-12-10T06:11:05.051373Z",
        "end_timestamp": "2025-12-10T06:11:15.779540Z",
        "is_drift": False,
        "is_simulated": True,
        "number_of_predictions": 100
    }
]
dm.write_window_metadata(
    Path('outputs/metadata/window_metadata.json'),
    windows
)
```

## Schema Validation Benefits

### 1. Early Error Detection
Invalid data is caught immediately with clear error messages:
```
ValidationError: Validation failed for schema 'prediction':
'feature3' is a required property
Path: input_features
```

### 2. Data Consistency
All components write data in the same format:
- Timestamps always ISO 8601
- Window IDs always sequential integers
- Feature names consistent across pipeline

### 3. Documentation
Schemas serve as machine-readable documentation:
- Required vs optional fields
- Data types and formats
- Valid value ranges

### 4. Version Management
Version suffixes (v1) allow future schema evolution:
- Add new optional fields without breaking old data
- Migrate data between schema versions
- Maintain backward compatibility

## Integration Test Coverage

| Test | Purpose | Status |
|------|---------|--------|
| Config Validation | All config files are valid | ✓ Pass |
| Model Service Health | Service is accessible | ✓ Pass |
| Prediction Logs | JSONL format valid | ✓ Pass |
| Window Metadata | Sequential IDs, valid structure | ✓ Pass |
| Drift Detection | Results match schema | ✓ Pass |
| Data Consistency | Window IDs align across files | ✓ Pass |
| Ground Truth | Detection accuracy metrics | ✓ Pass |
| Error Handling | Invalid data rejected | ✓ Pass |
| Existing Files | All current data valid | ✓ Pass |

## Validation Results

Current system data validation results:

```
✓ predictions_20251210.jsonl (1500 predictions)
✓ window_metadata.json (15 windows)
✓ drift_detection.json (15 windows, 4 drifts detected)
✓ config_simple.json
✓ config_multiple_drifts.json
✓ config_complex.json

Summary: 6/6 files passed validation
```

**Detection Performance:**
- True Positives: 2
- False Positives: 2
- True Negatives: 7
- False Negatives: 4
- Accuracy: 60.0%

## File Structure

```
drift-detector/
├── schemas/                          # NEW: Schema definitions
│   ├── prediction_v1.json           # Prediction schema
│   ├── window_metadata_v1.json      # Window metadata schema
│   ├── drift_detection_v1.json      # Drift detection schema
│   ├── config_v1.json               # Configuration schema
│   └── schema_registry.py           # Schema validation utilities
├── src/
│   ├── data_manager.py              # NEW: Unified data operations
│   ├── model_service.py
│   ├── drift_simulator.py
│   └── drift_detector.py
├── tests/                            # NEW: Integration tests
│   ├── __init__.py
│   └── test_integration.py          # End-to-end tests
├── configs/
│   ├── config_simple.json           # Validated ✓
│   ├── config_multiple_drifts.json  # Validated ✓
│   └── config_complex.json          # Validated ✓
├── logs/
│   └── predictions_*.jsonl          # Validated ✓
├── outputs/
│   ├── metadata/
│   │   └── window_metadata.json     # Validated ✓
│   └── detection/
│       └── drift_detection.json     # Validated ✓
└── EPIC5_IMPLEMENTATION.md          # This file
```

## Optional: Updating Existing Components

The current implementation is **non-breaking** - existing components work without changes. However, you can optionally update them to use the DataManager for additional safety:

### Example: Update drift_simulator.py

```python
# Current approach (still works):
with open(log_file, 'a') as f:
    f.write(json.dumps(prediction) + '\n')

# Enhanced approach with validation:
from src.data_manager import DataManager
dm = DataManager(validate=True)
dm.append_prediction(log_file, prediction)
```

This is **optional** since:
1. Current code already produces valid data (all files pass validation)
2. Lightweight research purpose doesn't require strict enforcement
3. Schema validation can be run separately via tests

## Future Enhancements

If you decide to expand the system, the schema foundation supports:

1. **Schema Migration Tools**
   - Automatically upgrade v1 → v2 data
   - Handle deprecated fields
   - Batch migration scripts

2. **Additional Schemas**
   - Model metadata schema
   - Experiment tracking schema
   - Performance metrics schema

3. **Strict Mode**
   - Require validation in all components
   - CI/CD pipeline integration
   - Pre-commit schema checks

4. **Database Integration**
   - Use schemas to generate database tables
   - Maintain JSON + DB dual storage
   - Query optimization for large datasets

## Summary

Epic 5 successfully implements:

✓ **Task 5.1**: Unified JSON storage schemas with versioning
✓ **Task 5.2**: End-to-end integration tests (11/11 passing)

**Key Deliverables:**
- 4 JSON Schema definitions
- Schema registry module with validation
- Data manager with unified operations
- Comprehensive integration test suite
- 100% validation pass rate on existing data

**Impact:**
- Data consistency guaranteed across pipeline
- Early error detection with clear messages
- Future-proof with versioning support
- Research-friendly lightweight approach
