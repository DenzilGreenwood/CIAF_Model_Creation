"""
Test runner script for CIAF - runs both frontend and backend tests.
Usage: python run_tests.py [--frontend] [--backend] [--coverage] [--watch]
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd: list, cwd: str = None, description: str = "") -> int:
    """Run a command and return exit code."""
    if description:
        print(f"\n{'='*70}")
        print(f"  {description}")
        print(f"{'='*70}\n")

    try:
        result = subprocess.run(cmd, cwd=cwd, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return 1


def run_frontend_tests(coverage: bool = False, watch: bool = False) -> int:
    """Run frontend tests."""
    frontend_dir = Path(__file__).parent / "frontend"

    # Use npx or npm depending on platform
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    if coverage:
        cmd = [npm_cmd, "run", "coverage"]
    elif watch:
        cmd = [npm_cmd, "run", "test", "--", "--watch"]
    else:
        cmd = [npm_cmd, "run", "test"]

    return run_command(
        cmd,
        cwd=str(frontend_dir),
        description="Running Frontend Tests (UI/UX and Hooks)",
    )


def run_backend_tests(coverage: bool = False, watch: bool = False) -> int:
    """Run backend tests."""
    vault_dir = Path(__file__).parent / "ciaf" / "vault"

    # Disable problematic plugins to avoid pydantic/langsmith compatibility issues
    cmd = ["pytest", "api.test.py", "-v", "-p", "no:langsmith"]

    if coverage:
        cmd.extend(["--cov=ciaf/vault", "--cov-report=html", "--cov-report=term"])

    if watch:
        cmd.append("--looponfail")

    return run_command(
        cmd,
        cwd=str(vault_dir),
        description="Running Backend Tests (Vault API)",
    )


def run_all_tests(coverage: bool = False, watch: bool = False) -> tuple[int, int]:
    """Run all tests."""
    print("\n" + "="*70)
    print("  CIAF COMPREHENSIVE TEST SUITE")
    print("="*70)

    frontend_result = run_frontend_tests(coverage=coverage, watch=watch)
    backend_result = run_backend_tests(coverage=coverage, watch=watch)

    return frontend_result, backend_result


def print_summary(frontend: int, backend: int):
    """Print test summary."""
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70 + "\n")

    frontend_status = "✅ PASSED" if frontend == 0 else "❌ FAILED"
    backend_status = "✅ PASSED" if backend == 0 else "❌ FAILED"

    print(f"Frontend Tests: {frontend_status}")
    print(f"Backend Tests:  {backend_status}")

    all_passed = frontend == 0 and backend == 0
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"

    print(f"\nOverall:        {overall_status}\n")

    return 0 if all_passed else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CIAF Test Runner - Frontend & Backend Tests"
    )

    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Run frontend tests only",
    )

    parser.add_argument(
        "--backend",
        action="store_true",
        help="Run backend tests only",
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage reports",
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run tests in watch mode (re-run on file changes)",
    )

    args = parser.parse_args()

    # Default to running both if no specific test type selected
    run_frontend = args.frontend or not (args.frontend or args.backend)
    run_backend = args.backend or not (args.frontend or args.backend)

    results = []

    if run_frontend:
        results.append(("Frontend", run_frontend_tests(args.coverage, args.watch)))

    if run_backend:
        results.append(("Backend", run_backend_tests(args.coverage, args.watch)))

    # Print summary
    print("\n" + "="*70)
    print("  FINAL TEST REPORT")
    print("="*70 + "\n")

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result == 0 else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if result != 0:
            all_passed = False

    if args.coverage:
        print("\n📊 Coverage Report:")
        print("   Frontend: frontend/coverage/")
        print("   Backend:  ciaf/vault/htmlcov/")

    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
