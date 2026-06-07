"""
Phase 8 smoke test script (API-level).

Usage:
python scripts/phase8_smoke_test.py --base-url http://localhost:8000 --username admin --password secret --year 2026 --month 5 --date 2026-05-29
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
    parser.add_argument("--recipient-group", default="admin", choices=["admin", "faculty", "all"])
    parser.add_argument("--force-send", action="store_true")
    args = parser.parse_args()

    login_url = f"{args.base_url}/api/v1/auth/login"
    with httpx.Client(timeout=45.0) as client:
        login_resp = client.post(login_url, json={"username": args.username, "password": args.password})
        if login_resp.status_code != 200:
            print("Login failed:", login_resp.status_code, login_resp.text)
            return 1

        token = login_resp.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})

        force_send_q = "true" if args.force_send else "false"
        checks = [
            (
                "POST",
                f"{args.base_url}/api/v1/attendance/reports/email/monthly"
                f"?year={args.year}&month={args.month}&recipient_group={args.recipient_group}&force_send={force_send_q}",
            ),
            (
                "POST",
                f"{args.base_url}/api/v1/attendance/reports/email/daily"
                f"?target_date={args.date}&recipient_group={args.recipient_group}&force_send={force_send_q}",
            ),
            ("GET", f"{args.base_url}/api/v1/attendance/reports/email/deliveries?limit=10"),
            ("GET", f"{args.base_url}/api/v1/attendance/reports/email/summary?last_n=30"),
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

