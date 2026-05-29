"""
Phase 10 final production-readiness validation runner.

This script orchestrates:
1) Phase 10 core pytest suites
2) API smoke test
3) Optional soak test

Usage:
python scripts/phase10_validation_runner.py --base-url http://localhost:8000 --username admin --password secret --date 2026-05-29 --department "Computer Science"
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def run_step(name: str, command: list[str]) -> int:
    print(f"\n=== {name} ===")
    print("Command:", " ".join(shlex.quote(part) for part in command))
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    print(f"Exit Code: {result.returncode}")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--month", type=int, default=5)
    parser.add_argument("--date", default="2026-05-29")
    parser.add_argument("--department", default="Computer Science")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--run-soak", action="store_true")
    parser.add_argument("--soak-seconds", type=int, default=120)
    parser.add_argument("--soak-interval-ms", type=int, default=500)
    args = parser.parse_args()

    failures: list[str] = []

    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "app/tests/test_setup.py",
        "app/tests/test_auth.py",
        "app/tests/test_student_routes.py",
        "app/tests/test_attendance_routes.py",
        "app/tests/test_dashboard_routes.py",
        "app/tests/test_diagnostics_routes.py",
        "app/tests/test_scheduler_routes.py",
        "app/tests/test_email_workflow.py",
        "-q",
    ]
    if run_step("Phase 10 Test Matrix", pytest_cmd) != 0:
        failures.append("Phase 10 Test Matrix")

    smoke_cmd = [
        sys.executable,
        "scripts/phase10_smoke_test.py",
        "--base-url",
        args.base_url,
        "--username",
        args.username,
        "--password",
        args.password,
        "--year",
        str(args.year),
        "--month",
        str(args.month),
        "--date",
        args.date,
        "--department",
        args.department,
        "--days",
        str(args.days),
    ]
    if run_step("Phase 10 API Smoke Test", smoke_cmd) != 0:
        failures.append("Phase 10 API Smoke Test")

    if args.run_soak:
        soak_cmd = [
            sys.executable,
            "scripts/phase10_soak_test.py",
            "--base-url",
            args.base_url,
            "--username",
            args.username,
            "--password",
            args.password,
            "--duration-seconds",
            str(args.soak_seconds),
            "--interval-ms",
            str(args.soak_interval_ms),
            "--date",
            args.date,
            "--department",
            args.department,
        ]
        if run_step("Phase 10 Soak Test", soak_cmd) != 0:
            failures.append("Phase 10 Soak Test")

    print("\n=== Final Result ===")
    if failures:
        print("Status: FAILED")
        for name in failures:
            print(f"- {name}")
        return 2

    print("Status: PASSED")
    print("Backend is demo-ready for Phase 10 validation scope.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

