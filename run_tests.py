#!/usr/bin/env python3
"""
Test runner for drift detection system.

Provides convenient commands to run different test suites.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def run_command(cmd):
    """Run command and return exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print("""
Usage: python run_tests.py <command>

Commands:
  all           - Run all tests
  unit          - Run unit tests only
  integration   - Run integration tests only
  epic1         - Run Epic 1 tests (model service)
  epic2         - Run Epic 2 tests (drift simulator)
  epic3         - Run Epic 3 tests (drift detector)
  epic5         - Run Epic 5 tests (schema & integration)
  coverage      - Run tests with coverage report
  fast          - Run fast tests only (skip slow tests)
  verbose       - Run with verbose output

Examples:
  python run_tests.py all
  python run_tests.py unit
  python run_tests.py coverage
        """)
        return 1

    command = sys.argv[1]
    project_root = Path(__file__).parent

    # Base pytest command
    pytest_cmd = [sys.executable, "-m", "pytest"]

    if command == "all":
        print_header("Running All Tests")
        return run_command(pytest_cmd + ["tests/"])

    elif command == "unit":
        print_header("Running Unit Tests")
        return run_command(pytest_cmd + ["tests/unit/"])

    elif command == "integration":
        print_header("Running Integration Tests")
        return run_command(pytest_cmd + ["tests/test_integration.py"])

    elif command == "epic1":
        print_header("Running Epic 1 Tests (Model Service)")
        return run_command(pytest_cmd + ["tests/unit/test_model_service.py"])

    elif command == "epic2":
        print_header("Running Epic 2 Tests (Drift Simulator)")
        return run_command(pytest_cmd + ["tests/unit/test_drift_simulator.py"])

    elif command == "epic3":
        print_header("Running Epic 3 Tests (Drift Detector)")
        return run_command(pytest_cmd + ["tests/unit/test_drift_detector.py"])

    elif command == "epic5":
        print_header("Running Epic 5 Tests (Schema & Integration)")
        return run_command(pytest_cmd + [
            "tests/unit/test_schema_validation.py",
            "tests/test_integration.py"
        ])

    elif command == "coverage":
        print_header("Running Tests with Coverage")
        return run_command(pytest_cmd + [
            "tests/",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    elif command == "fast":
        print_header("Running Fast Tests Only")
        return run_command(pytest_cmd + ["tests/", "-m", "not slow"])

    elif command == "verbose":
        print_header("Running All Tests (Verbose)")
        return run_command(pytest_cmd + ["tests/", "-vv", "-s"])

    else:
        print(f"Unknown command: {command}")
        print("Run 'python run_tests.py' for usage information")
        return 1


if __name__ == "__main__":
    sys.exit(main())
