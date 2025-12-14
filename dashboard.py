"""
Drift Detection Dashboard - Epic 4
Minimal MVP using Streamlit and Plotly for visualization.
"""
import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


# Page configuration
st.set_page_config(
    page_title="Drift Detection Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_predictions(log_file):
    """Load predictions from JSONL file."""
    predictions = []
    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                predictions.append(json.loads(line))
    return predictions


@st.cache_data
def load_window_metadata(metadata_file):
    """Load window metadata from JSON."""
    with open(metadata_file, 'r') as f:
        return json.load(f)


@st.cache_data
def load_drift_detection(detection_file):
    """Load drift detection results from JSON."""
    if not os.path.exists(detection_file):
        return None
    with open(detection_file, 'r') as f:
        return json.load(f)


def prepare_dataframe(predictions):
    """Convert predictions to pandas DataFrame."""
    df = pd.DataFrame(predictions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Extract features into separate columns
    features_df = pd.json_normalize(df['input_features'])
    df = pd.concat([df.drop('input_features', axis=1), features_df], axis=1)

    return df


def get_available_log_files():
    """Get list of available prediction log files."""
    if not os.path.exists("logs"):
        return []
    return sorted([f for f in os.listdir("logs") if f.endswith(".jsonl")], reverse=True)


def main():
    # Title and description
    st.title("📊 Drift Detection Dashboard")
    st.markdown("Monitor feature distributions and drift detection over time")

    # Sidebar for file selection and controls
    with st.sidebar:
        st.header("⚙️ Configuration")

        # File selection
        log_files = get_available_log_files()
        if not log_files:
            st.error("No prediction log files found in logs/")
            st.info("Please run drift simulation first to generate data.")
            st.stop()

        selected_log = st.selectbox(
            "Select Log File",
            log_files,
            help="Choose a prediction log file to analyze"
        )

        log_path = f"logs/{selected_log}"
        metadata_path = "outputs/metadata/window_metadata.json"
        detection_path = "outputs/detection/drift_detection.json"

        st.divider()

        # Load data
        try:
            predictions = load_predictions(log_path)
            df = prepare_dataframe(predictions)

            # Try to load optional files
            windows = None
            detections = None

            if os.path.exists(metadata_path):
                windows = load_window_metadata(metadata_path)

            if os.path.exists(detection_path):
                detections = load_drift_detection(detection_path)

        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()

        # Data info
        st.metric("Total Predictions", len(predictions))
        if windows:
            st.metric("Total Windows", len(windows))
        if detections:
            drift_count = sum(1 for d in detections if d['drift_detected'])
            st.metric("Drift Detected", f"{drift_count} windows")

        st.divider()

        # Feature selection (Task 4.1)
        feature_columns = [col for col in df.columns if col.startswith('feature')]
        selected_feature = st.selectbox(
            "Select Feature",
            feature_columns,
            help="Choose a feature to visualize"
        )

        # Time range filtering (Task 4.3)
        st.subheader("🕐 Time Range")

        if windows:
            max_windows = len(windows)
            window_range = st.slider(
                "Window Range",
                0, max_windows - 1,
                (0, max_windows - 1),
                help="Filter data by window range"
            )
        else:
            window_range = (0, len(df))

    # Main content area
    st.header(f"Feature: {selected_feature}")

    # Apply window filtering
    if windows:
        # Filter by window ID - use timestamp-based filtering instead
        start_window, end_window = window_range

        # Get timestamp range from windows
        if start_window < len(windows) and end_window < len(windows):
            start_time = pd.to_datetime(windows[start_window]['start_timestamp'])
            end_time = pd.to_datetime(windows[end_window]['end_timestamp'])

            filtered_df = df[
                (df['timestamp'] >= start_time) &
                (df['timestamp'] <= end_time)
            ]
        else:
            filtered_df = df
    else:
        filtered_df = df

    # Task 4.1: Feature Distribution Visualization
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Feature Over Time")

        # Time series plot
        fig_timeseries = go.Figure()

        fig_timeseries.add_trace(go.Scatter(
            x=filtered_df['timestamp'],
            y=filtered_df[selected_feature],
            mode='lines+markers',
            name=selected_feature,
            marker=dict(size=4),
            line=dict(width=1)
        ))

        # Add drift markers if available
        if detections and windows:
            drift_windows = [d['window_id'] for d in detections if d['drift_detected']]
            for window_id in drift_windows:
                if start_window <= window_id <= end_window and window_id < len(windows):
                    window = windows[window_id]
                    drift_time = pd.to_datetime(window['start_timestamp'])

                    # Add vertical line using shape instead of add_vline
                    fig_timeseries.add_shape(
                        type="line",
                        x0=drift_time,
                        x1=drift_time,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(color="red", width=2, dash="dash")
                    )

                    # Add annotation for the drift marker
                    fig_timeseries.add_annotation(
                        x=drift_time,
                        y=1,
                        yref="paper",
                        text="Drift",
                        showarrow=False,
                        yshift=10,
                        font=dict(color="red", size=10)
                    )

        fig_timeseries.update_layout(
            xaxis_title="Time",
            yaxis_title=f"{selected_feature} Value",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig_timeseries, use_container_width=True)

    with col2:
        st.subheader("Feature Distribution")

        # Histogram
        fig_hist = go.Figure()

        fig_hist.add_trace(go.Histogram(
            x=filtered_df[selected_feature],
            nbinsx=30,
            name=selected_feature,
            marker_color='steelblue'
        ))

        fig_hist.update_layout(
            xaxis_title=f"{selected_feature} Value",
            yaxis_title="Count",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig_hist, use_container_width=True)

    # Task 4.2: Drift Detection Visualization
    if detections and windows:
        st.divider()
        st.header("🎯 Drift Detection Results")

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Drift Statistic Over Time")

            # Filter detections by window range
            filtered_detections = [
                d for d in detections
                if start_window <= d['window_id'] <= end_window
            ]

            detection_df = pd.DataFrame(filtered_detections)
            detection_df['timestamp'] = pd.to_datetime(detection_df['timestamp'])

            fig_drift = go.Figure()

            # Drift statistic line
            fig_drift.add_trace(go.Scatter(
                x=detection_df['timestamp'],
                y=detection_df['drift_statistic'],
                mode='lines+markers',
                name='Drift Statistic',
                marker=dict(
                    size=8,
                    color=['red' if d else 'green' for d in detection_df['drift_detected']],
                ),
                line=dict(width=2)
            ))

            # Baseline mean reference
            fig_drift.add_hline(
                y=detection_df['baseline_mean'].iloc[0],
                line_dash="dot",
                line_color="gray",
                annotation_text="Baseline",
                annotation_position="right"
            )

            fig_drift.update_layout(
                xaxis_title="Time",
                yaxis_title="Drift Statistic",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig_drift, use_container_width=True)

        with col4:
            st.subheader("Detection vs Ground Truth")

            # Create comparison if ground truth available
            if 'ground_truth_drift' in detection_df.columns:
                comparison = detection_df[['window_id', 'drift_detected', 'ground_truth_drift']].copy()
                comparison['status'] = comparison.apply(
                    lambda row: 'True Positive' if row['drift_detected'] and row['ground_truth_drift']
                    else 'False Positive' if row['drift_detected'] and not row['ground_truth_drift']
                    else 'False Negative' if not row['drift_detected'] and row['ground_truth_drift']
                    else 'True Negative',
                    axis=1
                )

                # Bar chart of detection status
                status_counts = comparison['status'].value_counts()

                fig_comparison = go.Figure(data=[
                    go.Bar(
                        x=status_counts.index,
                        y=status_counts.values,
                        marker_color=['green', 'lightgreen', 'salmon', 'red'],
                        text=status_counts.values,
                        textposition='auto'
                    )
                ])

                fig_comparison.update_layout(
                    xaxis_title="Detection Status",
                    yaxis_title="Count",
                    height=400,
                    showlegend=False
                )

                st.plotly_chart(fig_comparison, use_container_width=True)

                # Metrics
                accuracy = (status_counts.get('True Positive', 0) + status_counts.get('True Negative', 0)) / len(comparison)
                col_a, col_b = st.columns(2)
                col_a.metric("Accuracy", f"{accuracy:.1%}")
                col_b.metric("Total Windows", len(comparison))
            else:
                st.info("Ground truth labels not available")

    # Data table
    st.divider()
    st.header("📋 Data Details")

    with st.expander("View Predictions Data"):
        st.dataframe(
            filtered_df[['timestamp', selected_feature, 'prediction', 'model_version']].head(100),
            use_container_width=True
        )

    if detections:
        with st.expander("View Detection Results"):
            st.dataframe(
                pd.DataFrame(filtered_detections).head(20),
                use_container_width=True
            )


if __name__ == "__main__":
    main()
