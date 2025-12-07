"""
Drift Simulator for Epic 2: Synthetic Stream & Drift Simulator
Generates synthetic data with configurable drift phases and streams to /predict endpoint.
"""
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np


class DriftPhaseConfig:
    """Configuration for a single drift phase."""

    def __init__(self, config: Dict):
        self.phase_id = config["phase_id"]
        self.name = config["name"]
        self.num_requests = config["num_requests"]
        self.is_drift = config["is_drift"]
        self.drift_type = config["drift_type"]
        self.distribution = config["distribution"]

    def generate_sample(self) -> Dict[str, float]:
        """Generate a single sample from this phase's distribution."""
        sample = {}
        for feature_name, params in self.distribution.items():
            value = np.random.normal(params["mean"], params["std"])
            sample[feature_name] = float(value)
        return sample


class DriftSimulator:
    """Main drift simulator that generates and streams data."""

    def __init__(self, config_path: str, predict_url: str = "http://localhost:8000/predict"):
        """
        Initialize drift simulator.

        Args:
            config_path: Path to configuration JSON file
            predict_url: URL of the /predict endpoint
        """
        self.predict_url = predict_url
        self.config = self._load_config(config_path)
        self.phases = [DriftPhaseConfig(phase) for phase in self.config["drift_phases"]]
        self.request_rate = self.config["simulation"]["request_rate"]
        self.total_requests = self.config["simulation"]["total_requests"]
        self.window_size = self.config["simulation"]["window_size"]

        # Statistics tracking
        self.requests_sent = 0
        self.requests_failed = 0
        self.current_phase_idx = 0
        self.current_phase_count = 0

        # Window metadata tracking
        self.window_metadata = []
        self.current_window_id = 0
        self.current_window_start_time = None
        self.current_window_predictions = 0

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        with open(config_path, "r") as f:
            return json.load(f)

    def get_current_phase(self) -> DriftPhaseConfig:
        """Get the current drift phase."""
        if self.current_phase_idx >= len(self.phases):
            # Wrap around or stay at last phase
            return self.phases[-1]

        phase = self.phases[self.current_phase_idx]

        # Check if we need to move to next phase
        if self.current_phase_count >= phase.num_requests:
            self.current_phase_idx += 1
            self.current_phase_count = 0
            if self.current_phase_idx < len(self.phases):
                phase = self.phases[self.current_phase_idx]
                print(f"\n→ Entering Phase {phase.phase_id}: {phase.name} (drift={phase.is_drift})")

        return phase

    def generate_request(self) -> tuple[Dict[str, float], int, bool, str]:
        """
        Generate a single request.

        Returns:
            Tuple of (features, phase_id, is_drift, drift_type)
        """
        phase = self.get_current_phase()
        features = phase.generate_sample()
        self.current_phase_count += 1

        return features, phase.phase_id, phase.is_drift, phase.drift_type

    def send_prediction_request(self, features: Dict[str, float]) -> Optional[Dict]:
        """
        Send prediction request to the model service.

        Args:
            features: Feature dictionary

        Returns:
            Response JSON or None if failed
        """
        try:
            response = requests.post(
                self.predict_url,
                json={"features": features},
                timeout=5
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.requests_failed += 1
            print(f"✗ Request failed: {e}")
            return None

    def update_window_metadata(self, phase_id: int, is_drift: bool):
        """Update window metadata when window completes."""
        if self.current_window_start_time is None:
            self.current_window_start_time = datetime.utcnow().isoformat() + "Z"

        self.current_window_predictions += 1

        # Check if window is complete
        if self.current_window_predictions >= self.window_size:
            end_time = datetime.utcnow().isoformat() + "Z"

            metadata = {
                "window_id": self.current_window_id,
                "start_timestamp": self.current_window_start_time,
                "end_timestamp": end_time,
                "is_drift": is_drift,
                "is_simulated": True,
                "number_of_predictions": self.current_window_predictions
            }

            self.window_metadata.append(metadata)

            # Reset for next window
            self.current_window_id += 1
            self.current_window_start_time = datetime.utcnow().isoformat() + "Z"
            self.current_window_predictions = 0

            print(f"  ✓ Window {metadata['window_id']} completed: {metadata['number_of_predictions']} predictions, drift={is_drift}")

    def save_window_metadata(self, output_path: str = "data/window_metadata.json"):
        """Save window metadata to JSON file."""
        Path(output_path).parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(self.window_metadata, f, indent=2)

        print(f"\n✓ Window metadata saved to {output_path}")
        print(f"  Total windows: {len(self.window_metadata)}")

    def run(self):
        """Run the drift simulation."""
        print("=" * 60)
        print("Drift Simulator - Epic 2")
        print("=" * 60)
        print(f"Configuration:")
        print(f"  Request rate: {self.request_rate} req/s")
        print(f"  Total requests: {self.total_requests}")
        print(f"  Window size: {self.window_size}")
        print(f"  Drift phases: {len(self.phases)}")
        print(f"  Predict endpoint: {self.predict_url}")
        print()

        # Verify service is running
        try:
            response = requests.get(self.predict_url.replace("/predict", "/"))
            print(f"✓ Model service is running: {response.json()['model_version']}")
        except requests.exceptions.RequestException:
            print("✗ Model service is not running!")
            print("  Please start the service first: python src/model_service.py")
            return

        print("\nStarting simulation...\n")
        start_time = time.time()
        phase = self.get_current_phase()
        print(f"→ Starting Phase {phase.phase_id}: {phase.name} (drift={phase.is_drift})")

        delay = 1.0 / self.request_rate if self.request_rate > 0 else 0

        for i in range(self.total_requests):
            # Generate and send request
            features, phase_id, is_drift, drift_type = self.generate_request()
            response = self.send_prediction_request(features)

            if response:
                self.requests_sent += 1
                self.update_window_metadata(phase_id, is_drift)

                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"  Progress: {i + 1}/{self.total_requests} requests sent")

            # Rate limiting
            if delay > 0:
                time.sleep(delay)

        # Handle final incomplete window
        if self.current_window_predictions > 0:
            end_time = datetime.utcnow().isoformat() + "Z"
            metadata = {
                "window_id": self.current_window_id,
                "start_timestamp": self.current_window_start_time,
                "end_timestamp": end_time,
                "is_drift": self.get_current_phase().is_drift,
                "is_simulated": True,
                "number_of_predictions": self.current_window_predictions
            }
            self.window_metadata.append(metadata)
            print(f"  ✓ Final window {metadata['window_id']} completed: {metadata['number_of_predictions']} predictions")

        # Save metadata
        self.save_window_metadata()

        # Summary
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("Simulation Complete")
        print("=" * 60)
        print(f"Total requests sent: {self.requests_sent}/{self.total_requests}")
        print(f"Failed requests: {self.requests_failed}")
        print(f"Success rate: {100 * self.requests_sent / self.total_requests:.1f}%")
        print(f"Elapsed time: {elapsed_time:.2f}s")
        print(f"Actual rate: {self.requests_sent / elapsed_time:.2f} req/s")
        print(f"Total windows: {len(self.window_metadata)}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run drift simulation")
    parser.add_argument(
        "--config",
        type=str,
        default="config_example.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000/predict",
        help="URL of the /predict endpoint"
    )

    args = parser.parse_args()

    simulator = DriftSimulator(args.config, args.url)
    simulator.run()


if __name__ == "__main__":
    main()
