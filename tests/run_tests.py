#!/usr/bin/env python3
"""
Test runner script for SMCP GitHub & Git Plugins

This script runs the test suite with coverage reporting.
"""
import subprocess
import sys
import os


def main():
    """Run the test suite"""
    # Ensure we're in the project root (one level up from tests/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=plugins",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-fail-under=100",
    ]
    
    # Add markers based on command line args
    if len(sys.argv) > 1:
        if "unit" in sys.argv:
            cmd.extend(["-m", "unit"])
        elif "integration" in sys.argv:
            cmd.extend(["-m", "integration"])
        elif "e2e" in sys.argv:
            cmd.extend(["-m", "e2e"])
        else:
            cmd.extend(sys.argv[1:])
    else:
        # Run all tests except those requiring external tools by default
        # Users can run integration/e2e tests explicitly
        cmd.extend(["-m", "unit"])
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

