"""
Phase 9 smoke test script (API-level).

Usage:
python scripts/phase9_smoke_test.py --base-url http://localhost:8000 --username admin --password secret --year 2026 --month 5 --date 2026-05-29
"""

from __future__ import annotations

import argparse
import json
import sys

import httpx


def call(client: httpx.Client, method: str, url: str):
    response = client.request(method, url)
    try:
        body = response.json()
    except Exception:
        body = {"raw": response.text}
    return response.status_code, body


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
    args = parser.parse_args()

    with httpx.Client(timeout=45.0) as client:
        login = client.post(
            f"{args.base_url}/api/v1/auth/login",
            json={"username": args.username, "password": args.password},
        )
        if login.status_code != 200:
            print("Login failed:", login.status_code, login.text)
            return 1
        token = login.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})

        checks = [
            ("GET", f"{args.base_url}/api/v1/dashboard/summary?target_date={args.date}&department={args.department}"),
            ("GET", f"{args.base_url}/api/v1/dashboard/stats/daily?target_date={args.date}&department={args.department}"),
            ("GET", f"{args.base_url}/api/v1/dashboard/stats/monthly?year={args.year}&month={args.month}&department={args.department}"),
            ("GET", f"{args.base_url}/api/v1/dashboard/stats/department?target_date={args.date}"),
            ("GET", f"{args.base_url}/api/v1/dashboard/graphs/weekly?end_date={args.date}&days={args.days}&department={args.department}"),
            ("GET", f"{args.base_url}/api/v1/dashboard/graphs/monthly?year={args.year}&month={args.month}&department={args.department}"),
            ("GET", f"{args.base_url}/api/v1/dashboard/graphs/department?target_date={args.date}"),
            ("GET", f"{args.base_url}/api/v1/dashboard/monitoring/summary"),
        ]

        all_ok = True
        for method, url in checks:
            status, body = call(client, method, url)
            ok = status < 400 and body.get("success") is True
            all_ok = all_ok and ok
            print(json.dumps({"method": method, "url": url, "status": status, "ok": ok, "body": body}, indent=2))

        return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(main())

