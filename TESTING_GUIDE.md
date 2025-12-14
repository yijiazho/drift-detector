# Testing Guide

## Quick Start

### Install Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio "httpx<0.28.0"
```

**Note:** httpx must be version <0.28.0 for compatibility with starlette 0.27.0's TestClient.

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/unit/test_model_service.py -v
pytest tests/unit/test_drift_simulator.py -v
pytest tests/unit/test_drift_detector.py -v
pytest tests/unit/test_schema_validation.py -v
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Use the test runner
python run_tests.py all
python run_tests.py unit
python run_tests.py epic1
python run_tests.py coverage
```

### Alternative: Run Without pytest

```bash
# Manual test script (Epic 1)
python tests/test_model_service_manual.py

# Integration tests (Epic 5)
python tests/test_integration.py
```

## Test Organization

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── pytest.ini                       # Pytest configuration
├── fixtures/                        # Test data files
│   ├── valid/                       # Valid test data
│   ├── invalid/                     # Invalid test data for error handling
│   └── edge_cases/                  # Edge case test data
├── unit/                            # Unit tests by component
│   ├── test_model_service.py        # Epic 1: 40+ tests
│   ├── test_drift_simulator.py      # Epic 2: 30+ tests
│   ├── test_drift_detector.py       # Epic 3: 35+ tests
│   └── test_schema_validation.py    # Epic 5: 30+ tests
├── test_integration.py              # Epic 5: 11 integration tests
└── test_model_service_manual.py     # Manual test script (original)
```

## Test Coverage

### Implemented Tests (145+ tests)

**Epic 1: Model Service** ✅ 
- TEST-MS-001: Model loading (7 tests)
- TEST-MS-002: Health check endpoint (6 tests)
- TEST-MS-003: Prediction with valid input (6 tests)
- TEST-MS-004: Prediction with invalid input (7 tests)
- TEST-MS-005: Prediction logging (7 tests)

**Epic 2: Drift Simulator** ✅
- TEST-DS-001: Configuration loading (4 tests)
- TEST-DS-002: Drift phase generation (5 tests)
- TEST-DS-003: Phase transition logic (4 tests)
- TEST-DS-004: Window metadata tracking (6 tests)
- TEST-DS-005: Request sending (3 tests)
- TEST-DS-006: Metadata saving (3 tests)

**Epic 3: Drift Detector** ✅
- TEST-DD-001: Prediction loading (4 tests)
- TEST-DD-002: Window creation (5 tests)
- TEST-DD-003: ADWIN drift detection (5 tests)
- TEST-DD-004: Window statistics (4 tests)
- TEST-DD-005: Ground truth comparison (5 tests)
- TEST-DD-006: Detection result format (3 tests)

**Epic 5: Schema Validation** ✅
- TEST-SV-001: Schema registry (5 tests)
- TEST-SV-002: Prediction validation (8 tests)
- TEST-SV-003: Window metadata validation (5 tests)
- TEST-SV-004: Drift detection validation (4 tests)
- TEST-SV-005: Config validation (5 tests)
- Additional validation helpers (4 tests)

**Epic 5: Integration Tests** ✅
- 11 comprehensive integration tests

## Test Fixtures

Common fixtures available in all tests (from conftest.py):

- `temp_dir` - Temporary directory for test files
- `sample_prediction` - Valid prediction entry
- `sample_predictions_list` - List of 100 predictions
- `sample_window_metadata` - Valid window metadata
- `sample_drift_detection` - Valid drift detection result
- `sample_config` - Valid configuration
- `sample_prediction_log_file` - JSONL file with predictions
- `sample_config_file` - Config JSON file
- `invalid_prediction` - Invalid prediction for error tests
- `malformed_json_file` - File with malformed JSON
- `project_root` - Project root directory
- `model_path` - Path to model file
- `metadata_path` - Path to metadata file

## Test Examples

### Running Specific Tests

```bash
# Run only tests for model loading
pytest tests/unit/test_model_service.py::TestModelLoading -v

# Run only a specific test
pytest tests/unit/test_model_service.py::TestModelLoading::test_model_loads_from_valid_pickle_file -v

# Run tests matching a pattern
pytest tests/ -k "validation" -v

# Run tests with specific marker
pytest tests/ -m "integration" -v
```

### Running with Different Options

```bash
# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l

# Parallel execution (requires pytest-xdist)
pytest tests/ -n auto

# Only show failures
pytest tests/ --tb=short

# Quiet mode
pytest tests/ -q
```

## Common Test Patterns

### Testing Functions

```python
def test_function_name_descriptive():
    """Test description of what's being tested."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Testing with Fixtures

```python
def test_using_fixture(sample_prediction):
    """Test using a fixture."""
    assert "timestamp" in sample_prediction
    assert sample_prediction["prediction"] >= 0
```

### Testing Exceptions

```python
def test_invalid_input_raises_error():
    """Test that invalid input raises appropriate error."""
    with pytest.raises(ValueError):
        function_that_should_fail(invalid_input)
```

### Testing with Mocks

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using a mock."""
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked result"
        result = code_using_function()
        assert mock_func.called
```

## Troubleshooting

### Tests Skipped

Some tests are skipped if prerequisites aren't met:

- Model service tests skip if service not running
- Model loading tests skip if model files don't exist

Run `python create_model.py` to create model files.

### Import Errors

If you see import errors, make sure you're in the project root:

```bash
cd /Users/yijzhou/workplace/drift-detector
pytest tests/
```

### Fixture Not Found

Make sure `conftest.py` exists in the tests directory. Pytest automatically discovers it.

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Next Steps

1. Install pytest: `pip install pytest pytest-cov`
2. Run tests: `python run_tests.py all`
3. Check coverage: `python run_tests.py coverage`
4. Review test output and fix any failures
5. Add more tests as needed

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest markers](https://docs.pytest.org/en/stable/mark.html)
- [Test Plan](TEST_PLAN.md) - Full test specifications
- [Test Plan Summary](TEST_PLAN_SUMMARY.md) - Implementation guide
