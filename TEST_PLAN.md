# Comprehensive Test Plan - Drift Detection System

## Overview

This document outlines comprehensive test cases for the entire drift detection system across all 5 epics. Tests are organized by component and priority level.

## Test Organization

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component interaction testing
- **End-to-End Tests**: Full pipeline testing
- **Performance Tests**: Load and stress testing
- **Edge Case Tests**: Boundary conditions and error handling

---

## Epic 1: Model Service Tests

### Unit Tests - Model Service

#### TEST-MS-001: Model Loading on Startup
**Priority**: Critical
**Component**: `model_service.py` - `load_model()`

**Test Cases**:
1. test_model_loads_from_valid_pickle_file
2. test_metadata_loads_from_valid_pickle_file
3. test_error_when_model_file_missing
4. test_error_when_metadata_file_missing
5. test_error_when_model_file_corrupted
6. test_model_version_extracted_correctly
7. test_feature_names_extracted_correctly

**Expected Results**:
- Valid files load without errors
- Missing/corrupted files raise appropriate exceptions
- Metadata correctly populated in global variables

#### TEST-MS-002: Health Check Endpoint
**Priority**: Critical
**Component**: `model_service.py` - `root()`

**Test Cases**:
1. test_health_check_returns_200_status
2. test_health_check_contains_status_running
3. test_health_check_contains_model_version
4. test_health_check_contains_service_name
5. test_health_check_before_model_loaded
6. test_health_check_after_model_loaded

**Expected Results**:
```json
{
  "status": "running",
  "model_version": "v1.0",
  "service": "Drift Detection Model Service"
}
```

#### TEST-MS-003: Prediction Endpoint with Valid Input
**Priority**: Critical
**Component**: `model_service.py` - `predict()`

**Test Cases**:
1. test_predict_accepts_valid_three_features
2. test_prediction_value_between_zero_and_one
3. test_response_contains_iso8601_timestamp
4. test_response_contains_model_version
5. test_multiple_sequential_predictions_succeed
6. test_concurrent_predictions_thread_safe

**Input**:
```json
{
  "features": {
    "feature1": 3.5,
    "feature2": 1.2,
    "feature3": 0.8
  }
}
```

**Expected Output**:
```json
{
  "prediction": 0.5,  // float between 0-1
  "model_version": "v1.0",
  "timestamp": "2025-12-13T10:00:00Z"
}
```

#### TEST-MS-004: Prediction Endpoint with Invalid Input
**Priority**: High
**Component**: `model_service.py` - `predict()`

**Test Cases**:
1. test_predict_rejects_missing_features_422
2. test_predict_ignores_extra_features_gracefully
3. test_predict_handles_wrong_feature_names
4. test_predict_rejects_non_numeric_values
5. test_predict_rejects_empty_request_body
6. test_predict_rejects_malformed_json_400
7. test_predict_validates_required_fields

**Expected Results**:
- Appropriate HTTP error codes (400, 422, 500)
- Clear error messages in response

#### TEST-MS-005: Prediction Logging Functionality
**Priority**: Critical
**Component**: `model_service.py` - `log_prediction()`

**Test Cases**:
1. test_prediction_logged_to_jsonl_file
2. test_log_filename_includes_date_yyyymmdd
3. test_log_entry_contains_all_required_fields
4. test_log_entry_is_valid_json_format
5. test_multiple_predictions_append_correctly
6. test_logs_directory_created_if_missing
7. test_log_file_has_write_permissions

**Expected Log Entry**:
```json
{
  "timestamp": "2025-12-13T10:00:00Z",
  "input_features": {"feature1": 3.5, "feature2": 1.2, "feature3": 0.8},
  "prediction": 0.5,
  "model_version": "v1.0",
  "drift_phase": 1
}
```

### Integration Tests - Model Service

#### MS-I01: End-to-End Prediction Flow
**Priority**: Critical
**Components**: Full model service

**Test Cases**:
1. Start service → health check → prediction → verify log
2. Multiple clients making concurrent predictions
3. Service restart preserves logs
4. Large batch of predictions (1000+)

**Success Criteria**:
- All predictions logged correctly
- No data loss
- Consistent performance

---

## Epic 2: Drift Simulator Tests

### Unit Tests - Drift Simulator

#### DS-U01: Configuration Loading
**Priority**: Critical
**Component**: `drift_simulator.py` - `_load_config()`

**Test Cases**:
1. Valid JSON config loads successfully
2. Invalid JSON raises error
3. Missing required fields detected
4. Config validation for required keys
5. Default values applied correctly

**Valid Config Structure**:
```json
{
  "simulation": {
    "request_rate": 20,
    "total_requests": 400,
    "window_size": 100
  },
  "drift_phases": [...]
}
```

#### DS-U02: Drift Phase Generation
**Priority**: Critical
**Component**: `drift_simulator.py` - `DriftPhaseConfig.generate_sample()`

**Test Cases**:
1. Samples follow normal distribution
2. Mean matches config specification
3. Std dev matches config specification
4. All features present in sample
5. Values are numeric (float)
6. Multiple samples from same phase are different
7. Statistical properties converge over many samples

**Verification**:
- Generate 1000 samples
- Verify mean ≈ configured mean (±10%)
- Verify std ≈ configured std (±10%)

#### DS-U03: Phase Transition Logic
**Priority**: High
**Component**: `drift_simulator.py` - `get_current_phase()`

**Test Cases**:
1. Starts in first phase
2. Transitions to next phase after num_requests
3. Stays in final phase after all requests
4. Phase counter resets on transition
5. Phase announcements printed correctly

**Expected Behavior**:
- Phase 1: requests 0-199
- Phase 2: requests 200-399
- Total: 400 requests

#### DS-U04: Window Metadata Tracking
**Priority**: Critical
**Component**: `drift_simulator.py` - `update_window_metadata()`

**Test Cases**:
1. Window completes after window_size predictions
2. Window ID increments sequentially
3. Timestamps captured correctly
4. is_drift flag matches current phase
5. is_simulated always true
6. number_of_predictions accurate
7. Incomplete final window handled

**Expected Metadata**:
```json
{
  "window_id": 0,
  "start_timestamp": "2025-12-13T10:00:00Z",
  "end_timestamp": "2025-12-13T10:05:00Z",
  "is_drift": false,
  "is_simulated": true,
  "number_of_predictions": 100
}
```

#### DS-U05: Request Sending
**Priority**: High
**Component**: `drift_simulator.py` - `send_prediction_request()`

**Test Cases**:
1. Successful request returns response
2. Failed request increments failure counter
3. Request timeout handled gracefully
4. Network error handled gracefully
5. Invalid URL handled gracefully
6. Retry logic (if implemented)

### Integration Tests - Drift Simulator

#### DS-I01: Full Simulation Run
**Priority**: Critical
**Components**: Complete simulator + model service

**Test Cases**:
1. Simple config (2 phases) completes successfully
2. Complex config (3+ phases) completes successfully
3. All requests sent successfully
4. All windows created correctly
5. Metadata file written correctly
6. Model service receives all requests
7. Predictions logged for all requests

**Success Criteria**:
- Success rate ≥ 99%
- All windows accounted for
- Metadata matches expectations

#### DS-I02: Rate Limiting
**Priority**: Medium
**Components**: Simulator timing

**Test Cases**:
1. Request rate honored (20 req/s → ~50ms between requests)
2. Actual rate within 10% of configured rate
3. High rate (100 req/s) handled
4. Low rate (1 req/s) handled
5. Zero delay handled

**Verification**:
- Measure elapsed time vs expected time
- Verify variance is acceptable

---

## Epic 3: Drift Detector Tests

### Unit Tests - Drift Detector

#### DD-U01: Prediction Loading
**Priority**: Critical
**Component**: `drift_detector.py` - `load_predictions()`

**Test Cases**:
1. Valid JSONL file loads successfully
2. Empty file returns empty list
3. Malformed JSON line raises error
4. Empty lines ignored
5. Large file (10,000+ lines) loads efficiently
6. Missing file raises FileNotFoundError

#### DD-U02: Window Creation
**Priority**: Critical
**Component**: `drift_detector.py` - `create_windows()`

**Test Cases**:
1. Predictions divided into correct window sizes
2. Window IDs sequential starting from 0
3. Final incomplete window handled
4. Empty predictions list handled
5. Metadata matched to windows correctly
6. Window count calculation correct

**Example**:
- 250 predictions, window_size=100 → 3 windows (100, 100, 50)

#### DD-U03: ADWIN Drift Detection
**Priority**: Critical
**Component**: `drift_detector.py` - `detect_drift_in_window()`

**Test Cases**:
1. No drift in stable data
2. Drift detected in shifted data
3. Baseline set from first window
4. Drift statistic calculated correctly
5. ADWIN delta parameter affects sensitivity
6. Multiple drifts in sequence detected

**Test Data**:
- Window 1: mean=0.08, std=0.08 (baseline)
- Window 2: mean=0.08, std=0.08 (no drift)
- Window 3: mean=0.50, std=0.30 (drift!)

**Expected**:
- Window 1: drift_detected=false
- Window 2: drift_detected=false
- Window 3: drift_detected=true, drift_statistic≈0.42

#### DD-U04: Window Statistics
**Priority**: High
**Component**: `drift_detector.py` - `WindowedPredictions`

**Test Cases**:
1. Mean calculated correctly
2. Std calculated correctly
3. Count returns correct number
4. Timestamp extracted from last prediction
5. Empty window handled

**Test Data**:
```python
predictions = [0.1, 0.2, 0.3, 0.4, 0.5]
```

**Expected**:
- mean = 0.3
- std ≈ 0.1414
- count = 5

#### DD-U05: Ground Truth Comparison
**Priority**: Medium
**Component**: `drift_detector.py` - `print_summary()`

**Test Cases**:
1. Accuracy calculated correctly
2. True positives counted correctly
3. False positives counted correctly
4. True negatives counted correctly
5. False negatives counted correctly
6. Precision calculated correctly
7. Recall calculated correctly
8. Works when ground truth missing

**Test Scenario**:
```
Ground Truth: [F, F, T, T]
Detected:     [F, T, T, F]
```

**Expected**:
- TP=1, FP=1, TN=1, FN=1
- Accuracy=50%
- Precision=50%
- Recall=50%

### Integration Tests - Drift Detector

#### DD-I01: Full Detection Pipeline
**Priority**: Critical
**Components**: Complete drift detector

**Test Cases**:
1. Load predictions → create windows → detect → save results
2. Large dataset (10,000+ predictions) processed efficiently
3. Detection results match expected format
4. Output file written correctly
5. Summary statistics accurate

**Success Criteria**:
- All windows processed
- Results saved to JSON
- No data loss

---

## Epic 4: Dashboard Tests

### Unit Tests - Dashboard

#### DB-U01: Data Loading
**Priority**: Critical
**Component**: `dashboard.py` - loading functions

**Test Cases**:
1. load_predictions() loads JSONL correctly
2. load_window_metadata() loads JSON correctly
3. load_drift_detection() loads JSON correctly
4. Missing files handled gracefully
5. Malformed data raises appropriate error
6. Caching works (@st.cache_data)

#### DB-U02: DataFrame Preparation
**Priority**: High
**Component**: `dashboard.py` - `prepare_dataframe()`

**Test Cases**:
1. Timestamps converted to datetime
2. Features extracted to separate columns
3. Original structure preserved
4. Column names correct
5. Data types correct

#### DB-U03: File Discovery
**Priority**: Medium
**Component**: `dashboard.py` - `get_available_log_files()`

**Test Cases**:
1. Lists all .jsonl files in logs/
2. Returns empty list if no files
3. Returns empty list if logs/ missing
4. Files sorted in reverse chronological order

### UI/Functional Tests - Dashboard

#### DB-F01: Feature Visualization
**Priority**: Critical
**Component**: Feature distribution charts

**Test Cases**:
1. Time series plot displays correctly
2. Histogram displays correctly
3. Feature selection dropdown works
4. Drift markers appear on time series
5. Charts update when feature changed
6. Hover tooltips work

#### DB-F02: Drift Detection Visualization
**Priority**: Critical
**Component**: Drift detection charts

**Test Cases**:
1. Drift statistic chart displays
2. Ground truth comparison chart displays
3. Detection markers colored correctly (red=drift, green=stable)
4. Baseline reference line shown
5. Accuracy metrics calculated correctly

#### DB-F03: Time Range Filtering
**Priority**: High
**Component**: Window range slider

**Test Cases**:
1. Slider limits correct (0 to max_windows-1)
2. Data filters correctly when slider moved
3. All charts update together
4. Full range shows all data
5. Partial range shows subset

#### DB-F04: Data Tables
**Priority**: Medium
**Component**: Expandable data views

**Test Cases**:
1. Predictions table displays correctly
2. Detection results table displays correctly
3. Tables expand/collapse
4. Pagination works for large datasets
5. Column headers correct

---

## Epic 5: Schema & Integration Tests

### Unit Tests - Schema Validation

#### SV-U01: Schema Registry
**Priority**: Critical
**Component**: `schemas/schema_registry.py`

**Test Cases**:
1. All schemas load successfully
2. get_schema() returns correct schema
3. get_schema() raises KeyError for invalid name
4. list_schemas() returns all schema names
5. Global registry singleton works

#### SV-U02: Prediction Validation
**Priority**: Critical
**Component**: Schema validation for predictions

**Test Cases**:
1. Valid prediction passes validation
2. Missing timestamp fails
3. Missing input_features fails
4. Missing feature1/2/3 fails
5. Invalid timestamp format fails
6. Prediction outside 0-1 range fails
7. Invalid model_version format fails
8. Extra fields handled (additionalProperties)

**Valid Example**:
```json
{
  "timestamp": "2025-12-13T10:00:00Z",
  "input_features": {
    "feature1": 3.5,
    "feature2": 1.2,
    "feature3": 0.8
  },
  "prediction": 0.5,
  "model_version": "v1.0",
  "drift_phase": 1
}
```

#### SV-U03: Window Metadata Validation
**Priority**: Critical
**Component**: Schema validation for windows

**Test Cases**:
1. Valid window metadata passes
2. Missing window_id fails
3. Negative window_id fails
4. Invalid timestamp format fails
5. Missing required boolean fields fails
6. Invalid number_of_predictions fails

#### SV-U04: Drift Detection Validation
**Priority**: Critical
**Component**: Schema validation for detections

**Test Cases**:
1. Valid detection result passes
2. Missing required fields fail
3. Negative drift_statistic fails
4. Negative current_std fails
5. Invalid predictions_processed fails

#### SV-U05: Config Validation
**Priority**: Critical
**Component**: Schema validation for configs

**Test Cases**:
1. Valid config passes validation
2. Missing simulation section fails
3. Invalid request_rate (0 or negative) fails
4. Invalid drift_type fails
5. Missing drift phases fails
6. Invalid distribution params fail

### Unit Tests - Data Manager

#### DM-U01: Prediction Operations
**Priority**: Critical
**Component**: `src/data_manager.py` - prediction methods

**Test Cases**:
1. append_prediction() validates and writes
2. append_prediction() creates directory if needed
3. read_predictions() loads and validates JSONL
4. Invalid prediction rejected during append
5. Invalid data rejected during read
6. Validation can be disabled per-operation

#### DM-U02: Window Metadata Operations
**Priority**: Critical
**Component**: `src/data_manager.py` - window methods

**Test Cases**:
1. write_window_metadata() validates and writes
2. write uses atomic write (temp + rename)
3. read_window_metadata() loads and validates
4. Invalid metadata rejected during write
5. Array of windows validated correctly

#### DM-U03: Drift Detection Operations
**Priority**: Critical
**Component**: `src/data_manager.py` - detection methods

**Test Cases**:
1. write_drift_detections() validates and writes
2. Atomic write works correctly
3. read_drift_detections() loads and validates
4. All required fields validated

#### DM-U04: File Validation
**Priority**: High
**Component**: `src/data_manager.py` - validate_existing_files()

**Test Cases**:
1. All valid files pass
2. Invalid files detected
3. Returns correct results dict
4. Verbose mode prints correctly
5. Missing files handled gracefully

### Integration Tests - Epic 5

#### E5-I01: Configuration Validation
**Priority**: Critical
**Components**: All config files

**Test Cases**:
1. config_simple.json validates
2. config_multiple_drifts.json validates
3. config_complex.json validates
4. Invalid configs rejected

#### E5-I02: Model Service Health
**Priority**: High
**Components**: Model service + integration tests

**Test Cases**:
1. Service responds to health check
2. Model version returned correctly
3. Service unavailable handled gracefully

#### E5-I03: Prediction Log Validation
**Priority**: Critical
**Components**: Prediction logs + validation

**Test Cases**:
1. All prediction logs validate
2. JSONL format correct
3. Schema compliance verified
4. Empty lines handled

#### E5-I04: Window Metadata Validation
**Priority**: Critical
**Components**: Window metadata + validation

**Test Cases**:
1. Window IDs sequential
2. Timestamps valid
3. All required fields present
4. Drift flags valid

#### E5-I05: Drift Detection Validation
**Priority**: Critical
**Components**: Detection results + validation

**Test Cases**:
1. Detection results validate
2. Window IDs align with metadata
3. Statistics in valid ranges
4. Ground truth present when available

#### E5-I06: Data Consistency
**Priority**: Critical
**Components**: Cross-file consistency

**Test Cases**:
1. Window count matches across files
2. Window IDs align
3. Prediction counts match
4. Timestamps aligned

#### E5-I07: Ground Truth Comparison
**Priority**: High
**Components**: Metadata + detection results

**Test Cases**:
1. TP/FP/TN/FN calculated correctly
2. Accuracy computed correctly
3. Precision/recall computed correctly
4. Missing ground truth handled

---

## End-to-End Tests

### E2E-01: Complete Pipeline
**Priority**: Critical
**Components**: All epics

**Test Scenario**:
1. Start model service
2. Run drift simulator with simple config
3. Run drift detector on generated data
4. Launch dashboard and verify visualization
5. Run validation suite

**Success Criteria**:
- All components work together
- Data flows correctly
- No errors or data loss
- All validations pass

**Steps**:
```bash
# 1. Start service
python src/model_service.py &

# 2. Run simulation
python src/drift_simulator.py --config configs/config_simple.json

# 3. Detect drift
python src/drift_detector.py --log-file logs/predictions_YYYYMMDD.jsonl

# 4. Validate
python validate_epic5.py

# 5. Launch dashboard
streamlit run dashboard.py
```

### E2E-02: Multiple Scenarios
**Priority**: High
**Components**: All epics

**Test Cases**:
1. Simple drift scenario (baseline → abrupt drift)
2. Complex drift scenario (baseline → gradual → abrupt → recovery)
3. No drift scenario (stable throughout)
4. Multiple drift points scenario

**Verification**:
- Detection accuracy ≥ 60%
- No false positives when no drift
- Drift points correctly identified

### E2E-03: Large Scale
**Priority**: Medium
**Components**: All epics

**Test Scenario**:
- 10,000 predictions
- 100 windows
- Multiple drift phases
- High request rate (100 req/s)

**Success Criteria**:
- All predictions processed
- Performance acceptable (<30s total)
- Memory usage reasonable
- No crashes or errors

---

## Performance Tests

### PERF-01: Model Service Load
**Priority**: Medium
**Component**: Model service

**Test Cases**:
1. 1000 concurrent requests
2. 10,000 sequential requests
3. Sustained load (100 req/s for 5 minutes)
4. Memory usage under load
5. Response time distribution

**Acceptance Criteria**:
- Mean response time < 100ms
- 99th percentile < 500ms
- No memory leaks
- Success rate > 99.9%

### PERF-02: Drift Detection Performance
**Priority**: Medium
**Component**: Drift detector

**Test Cases**:
1. 1,000 predictions processed in < 1s
2. 10,000 predictions processed in < 5s
3. 100,000 predictions processed in < 60s
4. Memory usage scales linearly

### PERF-03: Dashboard Performance
**Priority**: Low
**Component**: Dashboard

**Test Cases**:
1. Load 10,000 predictions in < 5s
2. Chart rendering in < 2s
3. Filtering updates in < 1s
4. Multiple concurrent users (if applicable)

---

## Edge Cases & Error Handling

### EDGE-01: Empty Data
**Priority**: High
**Components**: All

**Test Cases**:
1. Empty prediction log file
2. Empty window metadata
3. Zero predictions in window
4. Zero windows
5. Empty config file

**Expected**: Graceful handling with clear error messages

### EDGE-02: Malformed Data
**Priority**: High
**Components**: All

**Test Cases**:
1. Corrupted JSONL file
2. Invalid JSON in config
3. Missing required fields
4. Wrong data types
5. Encoding issues (UTF-8, etc.)

**Expected**: Clear validation errors

### EDGE-03: Boundary Conditions
**Priority**: Medium
**Components**: All

**Test Cases**:
1. Single prediction
2. Single window
3. Maximum integer values
4. Very small numbers (near zero)
5. Very large numbers
6. Special float values (inf, nan)

### EDGE-04: Network Issues
**Priority**: Medium
**Components**: Simulator, Model Service

**Test Cases**:
1. Service unavailable
2. Connection timeout
3. Slow response
4. Network interruption mid-request
5. DNS failure

**Expected**: Retry logic, clear error messages

### EDGE-05: File System Issues
**Priority**: Medium
**Components**: All

**Test Cases**:
1. Disk full
2. Permission denied
3. Read-only filesystem
4. File locked by another process
5. Path too long
6. Invalid characters in filename

**Expected**: Appropriate error messages, no data corruption

---

## Security Tests

### SEC-01: Input Validation
**Priority**: High
**Components**: Model service, Simulator

**Test Cases**:
1. SQL injection attempts (if applicable)
2. XSS attempts (if applicable)
3. Path traversal attempts (../)
4. Command injection attempts
5. Large payload attacks (>10MB)
6. Malformed headers

**Expected**: Rejected with appropriate errors

### SEC-02: File Access
**Priority**: Medium
**Components**: All

**Test Cases**:
1. Cannot access files outside project directory
2. Cannot overwrite system files
3. File permissions respected
4. Symbolic link handling

---

## Test Execution Strategy

### Priority Levels

**P0 (Critical)**: Must pass before release
- All unit tests for core functionality
- All schema validation tests
- E2E happy path test

**P1 (High)**: Should pass before release
- Integration tests
- Error handling tests
- Most edge cases

**P2 (Medium)**: Nice to have
- Performance tests
- UI/UX tests
- Advanced edge cases

**P3 (Low)**: Future enhancement
- Load testing beyond normal usage
- Security stress tests
- Internationalization

### Test Execution Order

1. **Unit Tests** (by epic, in order)
   - Epic 1: Model Service
   - Epic 2: Drift Simulator
   - Epic 3: Drift Detector
   - Epic 4: Dashboard
   - Epic 5: Schema & Integration

2. **Integration Tests** (by epic)

3. **End-to-End Tests**

4. **Performance Tests**

5. **Edge Cases & Security**

### Automated Testing

**Recommended Tools**:
- pytest for Python unit/integration tests
- locust or Apache JMeter for load testing
- selenium for dashboard UI testing (optional)
- GitHub Actions for CI/CD

**Test Structure**:
```
tests/
├── unit/
│   ├── test_model_service.py
│   ├── test_drift_simulator.py
│   ├── test_drift_detector.py
│   ├── test_dashboard.py
│   └── test_schemas.py
├── integration/
│   ├── test_e2e_pipeline.py
│   ├── test_data_flow.py
│   └── test_validation.py
├── performance/
│   ├── test_load.py
│   └── test_scale.py
└── fixtures/
    ├── sample_predictions.jsonl
    ├── sample_windows.json
    └── sample_config.json
```

---

## Test Data Requirements

### Fixtures Needed

1. **Valid Prediction Log** (100 entries)
2. **Large Prediction Log** (10,000 entries)
3. **Window Metadata** (aligned with logs)
4. **Drift Detection Results** (aligned with windows)
5. **Config Files**:
   - Simple (2 phases)
   - Complex (5 phases)
   - Edge case (1 phase, 1 prediction)
6. **Invalid Data Examples**:
   - Malformed JSON
   - Missing fields
   - Wrong types

---

## Success Metrics

### Coverage Goals
- Unit test coverage: ≥ 80%
- Integration test coverage: ≥ 70%
- Critical path coverage: 100%

### Quality Metrics
- All P0 tests pass: 100%
- All P1 tests pass: ≥ 95%
- No critical bugs in production

### Performance Metrics
- Response time: < 100ms (p50), < 500ms (p99)
- Throughput: ≥ 100 req/s
- Memory usage: < 500MB for typical workload

---

## Test Maintenance

### When to Update Tests

1. **New Features**: Add tests before implementation (TDD)
2. **Bug Fixes**: Add regression test
3. **Schema Changes**: Update validation tests
4. **Performance Changes**: Update benchmarks

### Test Review Process

1. All new tests peer-reviewed
2. Flaky tests investigated and fixed
3. Obsolete tests removed
4. Coverage monitored in CI/CD

---

## Appendix: Test Templates

### Unit Test Template

```python
import pytest

class TestComponentName:
    """Tests for ComponentName functionality."""

    def test_function_name_happy_path(self):
        """Test normal operation."""
        # Arrange
        input_data = ...

        # Act
        result = function_under_test(input_data)

        # Assert
        assert result == expected_output

    def test_function_name_error_case(self):
        """Test error handling."""
        with pytest.raises(ExpectedException):
            function_under_test(invalid_input)
```

### Integration Test Template

```python
class TestIntegration:
    """Integration tests for component interaction."""

    @pytest.fixture
    def setup_environment(self):
        """Set up test environment."""
        # Setup code
        yield
        # Teardown code

    def test_integration_scenario(self, setup_environment):
        """Test components working together."""
        # Test scenario
        assert outcome == expected
```

---

## Summary

This test plan provides comprehensive coverage of the drift detection system across all 5 epics:

- **Epic 1**: 15 model service tests
- **Epic 2**: 12 drift simulator tests
- **Epic 3**: 14 drift detector tests
- **Epic 4**: 11 dashboard tests
- **Epic 5**: 22 schema & integration tests

**Total**: 74+ individual test cases

Implementation of these tests will ensure:
- Robust, production-ready code
- Confidence in changes and refactoring
- Clear documentation of expected behavior
- Early detection of regressions
