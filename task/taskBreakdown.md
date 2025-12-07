# Jira Task Breakdown -- Drift Detection System (With Data Schemas)

## Epic 1: Local Model Service

### Task 1.1: Set Up FastAPI Model Service

**Description:**\
Implement a FastAPI service that loads a pre-trained scikit-learn model
at startup and exposes a `/predict` endpoint.

**Request Payload Example:**

``` json
{
  "features": {
    "feature1": 3.5,
    "feature2": 1.2,
    "feature3": 0.8
  }
}
```

**Response Payload Example:**

``` json
{
  "prediction": 0.5,
  "model_version": "v1.0",
  "timestamp": "2025-11-21T10:00:00Z"
}
```

**Acceptance Criteria:** - FastAPI app runs locally. - Model loads
successfully at startup. - `/predict` endpoint is reachable via HTTP. -
Request and response match defined schemas.

------------------------------------------------------------------------

### Task 1.2: Implement Local Prediction Logging

**Description:**\
Log each prediction request/response into structured JSON storage.

**Logged Prediction Schema:**

``` json
{
  "timestamp": "2025-11-21T10:00:00Z",
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

**Acceptance Criteria:** - Logs match schema exactly. - Logs persist to
local JSON files. - Drift phase is properly recorded.

------------------------------------------------------------------------

## Epic 2: Synthetic Stream & Drift Simulator

### Task 2.1: Implement Synthetic Data Generator

**Description:**\
Create synthetic data generator for both normal and drift phases.

**Data Output Example:**

``` json
{
  "feature1": 4.1,
  "feature2": 0.9,
  "feature3": 1.3
}
```

**Acceptance Criteria:** - Baseline data follows stable distribution. -
Drift data reflects shifted mean/variance.

------------------------------------------------------------------------

### Task 2.2: Implement Drift Phase Annotation

**Description:**\
Add drift phase and drift labels for each generated window.

**Window Metadata Schema:**

``` json
{
  "window_id": 1,
  "start_timestamp": "2025-11-21T10:00:00Z",
  "end_timestamp": "2025-11-21T10:05:00Z",
  "is_drift": false,
  "is_simulated": true,
  "number_of_predictions": 100
}
```

**Acceptance Criteria:** - Each window includes `drift_phase` and
`is_drift`. - Metadata matches schema exactly.

------------------------------------------------------------------------

### Task 2.3: Implement Request Streaming to `/predict`

**Description:**\
Send generated data to `/predict` endpoint at a controlled rate.

**Acceptance Criteria:** - Rate is configurable. - All responses are
logged. - Failed requests are retried or recorded.

------------------------------------------------------------------------

## Epic 3: Drift Detection Engine

### Task 3.1: Implement Windowing Logic

**Description:**\
Group predictions into fixed-size windows for drift detection.

**Acceptance Criteria:** - Window size is configurable. - Windows
contain fixed number of records. - Window IDs are sequential.

------------------------------------------------------------------------

### Task 3.2: Implement ADWIN-Based Drift Detection

**Description:**\
Apply ADWIN drift detection on prediction streams.

**Acceptance Criteria:** - ADWIN processes windowed predictions. -
Produces drift statistic. - Drift flags generated correctly.

------------------------------------------------------------------------

### Task 3.3: Persist Drift Detection Output

**Description:**\
Save drift detection results into structured JSON storage.

**Drift Detection Output Schema:**

``` json
{
  "window_id": 1,
  "timestamp": "2025-11-21T10:05:00Z",
  "drift_statistic": 0.15,
  "drift_detected": false
}
```

**Acceptance Criteria:** - Output saved per window. - Schema is
validated. - Historical results persist.

------------------------------------------------------------------------

## Epic 4: Minimal Dashboard

### Task 4.1: Implement Feature Distribution Visualization

**Description:**\
Display feature distributions over time.

**Acceptance Criteria:** - Users select features dynamically. - Charts
auto-refresh. - Handles missing data gracefully.

------------------------------------------------------------------------

### Task 4.2: Implement Drift Detection Visualization

**Description:**\
Visualize drift statistics and detection flags.

**Acceptance Criteria:** - Drift points clearly marked. - True drift vs
detected drift visually distinct.

------------------------------------------------------------------------

### Task 4.3: Implement Time Range Filtering

**Description:**\
Allow users to select time ranges for analysis.

**Acceptance Criteria:** - Time filters apply to all visuals. -
Performance remains responsive.

------------------------------------------------------------------------

## Epic 5: Storage & Integration

### Task 5.1: Define Unified JSON Storage Schema

**Description:**\
Standardize schemas for predictions, windows, and drift output.

**Acceptance Criteria:** - All schemas documented. - Versioning
supported.

------------------------------------------------------------------------

### Task 5.2: Implement End-to-End Integration Test

**Description:**\
Validate full pipeline from simulation to dashboard.

**Acceptance Criteria:** - Data flows across all components. - Drift
simulation aligns with detection. - Dashboard reflects near real-time
updates.
