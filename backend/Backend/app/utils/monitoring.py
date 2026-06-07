"""Phase 10 Step 5-6: lightweight runtime monitoring and stability metrics."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock


_lock = Lock()
_request_count = 0
_error_count = 0
_total_response_time_ms = 0.0
_max_response_time_ms = 0.0
_recent_errors = deque(maxlen=100)
_startup_time = datetime.now(timezone.utc)


def record_request(*, duration_ms: float) -> None:
    global _request_count, _total_response_time_ms, _max_response_time_ms
    with _lock:
        _request_count += 1
        _total_response_time_ms += duration_ms
        if duration_ms > _max_response_time_ms:
            _max_response_time_ms = duration_ms


def record_error(*, error_type: str, path: str, status_code: int, request_id: str) -> None:
    global _error_count
    with _lock:
        _error_count += 1
        _recent_errors.appendleft(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_type": error_type,
                "path": path,
                "status_code": status_code,
                "request_id": request_id,
            }
        )


def get_runtime_metrics() -> dict:
    with _lock:
        avg = (_total_response_time_ms / _request_count) if _request_count > 0 else 0.0
        return {
            "uptime_seconds": int((datetime.now(timezone.utc) - _startup_time).total_seconds()),
            "request_count": _request_count,
            "error_count": _error_count,
            "error_rate_pct": round((_error_count / _request_count) * 100, 2) if _request_count else 0.0,
            "avg_response_time_ms": round(avg, 2),
            "max_response_time_ms": round(_max_response_time_ms, 2),
            "recent_errors": list(_recent_errors),
        }


def get_stability_snapshot() -> dict:
    metrics = get_runtime_metrics()
    healthy_error_rate = metrics["error_rate_pct"] <= 10.0
    healthy_latency = metrics["avg_response_time_ms"] <= 1000.0 if metrics["request_count"] > 0 else True
    status = "stable" if (healthy_error_rate and healthy_latency) else "degraded"
    return {
        "status": status,
        "checks": {
            "error_rate_ok": healthy_error_rate,
            "latency_ok": healthy_latency,
        },
        "metrics": metrics,
    }

