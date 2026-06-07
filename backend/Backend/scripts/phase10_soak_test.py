"""
Phase 10 soak test script (stability validation).

Usage:
python scripts/phase10_soak_test.py --base-url http://localhost:8000 --username admin --password secret --duration-seconds 120 --interval-ms 500
"""

from __future__ import annotations

import argparse
import statistics
import time

import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--duration-seconds", type=int, default=120)
    parser.add_argument("--interval-ms", type=int, default=500)
    parser.add_argument("--date", default="2026-05-29")
    parser.add_argument("--department", default="Computer Science")
    args = parser.parse_args()

    endpoints = [
        f"/api/v1/health",
        f"/api/v1/dashboard/summary?target_date={args.date}&department={args.department}",
        f"/api/v1/dashboard/graphs/weekly?end_date={args.date}&days=7&department={args.department}",
        f"/api/v1/attendance/automation/summary?last_n=20",
        f"/api/v1/diagnostics/metrics",
    ]

    latencies = []
    total = 0
    failures = 0
    end_at = time.time() + args.duration_seconds

    with httpx.Client(timeout=30.0) as client:
        login = client.post(
            f"{args.base_url}/api/v1/auth/login",
            json={"username": args.username, "password": args.password},
        )
        if login.status_code != 200:
            print("Login failed:", login.status_code, login.text)
            return 1
        token = login.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})

        idx = 0
        while time.time() < end_at:
            url = f"{args.base_url}{endpoints[idx % len(endpoints)]}"
            idx += 1
            start = time.perf_counter()
            try:
                response = client.get(url)
                body = response.json()
                ok = response.status_code < 400 and body.get("success") is True
                if not ok:
                    failures += 1
            except Exception:
                failures += 1
            finally:
                elapsed = (time.perf_counter() - start) * 1000
                latencies.append(elapsed)
                total += 1
            time.sleep(max(args.interval_ms / 1000.0, 0))

    fail_rate = (failures / total * 100) if total else 100.0
    avg_latency = statistics.mean(latencies) if latencies else 0.0
    p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else (max(latencies) if latencies else 0.0)

    print(
        {
            "total_requests": total,
            "failures": failures,
            "failure_rate_pct": round(fail_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "duration_seconds": args.duration_seconds,
        }
    )

    return 0 if fail_rate <= 5.0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

