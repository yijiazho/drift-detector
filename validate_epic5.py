#!/usr/bin/env python3
"""
Quick validation script for Epic 5 implementation.
Runs data validation and integration tests.
"""

import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def main():
    """Run all Epic 5 validation checks."""
    project_root = Path(__file__).parent

    print_header("EPIC 5: STORAGE & INTEGRATION - VALIDATION")

    # Test 1: Validate existing data files
    print_header("Step 1: Validating Existing Data Files")
    result1 = subprocess.run(
        [sys.executable, str(project_root / 'src' / 'data_manager.py')],
        cwd=project_root
    )

    # Test 2: Run integration tests
    print_header("Step 2: Running Integration Tests")
    result2 = subprocess.run(
        [sys.executable, str(project_root / 'tests' / 'test_integration.py')],
        cwd=project_root
    )

    # Summary
    print_header("VALIDATION COMPLETE")

    if result1.returncode == 0 and result2.returncode == 0:
        print("✓ All validation checks passed!")
        print("\nEpic 5 Implementation Status:")
        print("  ✓ Task 5.1: Unified JSON storage schemas")
        print("  ✓ Task 5.2: End-to-end integration tests")
        print("\nNext Steps:")
        print("  - Use DataManager for schema-validated data operations")
        print("  - Run 'python validate_epic5.py' to verify data integrity")
        print("  - See EPIC5_IMPLEMENTATION.md for detailed documentation")
        return 0
    else:
        print("✗ Some validation checks failed")
        print("Please review the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
