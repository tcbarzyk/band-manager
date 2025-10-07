#!/usr/bin/env python3
"""
Test runner script for the Band Manager API.

This script provides convenient ways to run different types of tests
and includes options for coverage reporting and test filtering.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def get_python_command():
    """Get the correct Python command for the current environment"""
    # Try to find the virtual environment python first
    venv_python = Path(__file__).parent / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    
    # Fallback to system python
    return sys.executable

def run_command(cmd, description):
    """Run a command and handle the output"""
    print(f"\n🚀 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return 1
    """Run a command and handle the output"""
    print(f"\n🚀 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Run Band Manager API tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "api", "repository"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests"
    )
    parser.add_argument(
        "--file",
        help="Run tests from specific file"
    )
    parser.add_argument(
        "--test",
        help="Run specific test function"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    python_cmd = get_python_command()
    cmd = [python_cmd, "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=70"
        ])
    
    # Add test filtering
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Add specific file or test
    if args.file:
        cmd.append(f"tests/{args.file}")
    elif args.test:
        cmd.extend(["-k", args.test])
    elif args.type != "all":
        if args.type == "unit":
            cmd.extend(["-m", "unit"])
        elif args.type == "integration":
            cmd.extend(["-m", "integration"])
        elif args.type == "api":
            cmd.append("tests/test_api.py")
        elif args.type == "repository":
            cmd.append("tests/test_repository.py")
    else:
        cmd.append("tests/")
    
    # Run the tests
    print("🧪 Band Manager API Test Runner")
    print("=" * 50)
    
    exit_code = run_command(cmd, f"Running {args.type} tests")
    
    if args.coverage and exit_code == 0:
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)