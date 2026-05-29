from datetime import date
from types import SimpleNamespace

from app.services import auto_absent_service


def test_identify_unmarked_student_ids():
    all_student_ids = [1, 2, 3, 4, 5]
    marked_ids = {2, 5}
    unmarked = auto_absent_service.identify_unmarked_student_ids(all_student_ids, marked_ids)
    assert unmarked == [1, 3, 4]


def test_resolve_target_date_with_explicit_date():
    target = date(2026, 5, 29)
    resolved = auto_absent_service.resolve_target_date(target_date=target)
    assert resolved == target


def test_auto_absent_result_default_execution_skipped_flag():
    result = auto_absent_service.AutoAbsentResult(
        run_date="2026-05-29",
        total_students=0,
        already_marked=0,
        auto_absent_marked=0,
        duplicate_skipped=0,
        excel_synced=0,
        status="success",
    )
    assert result.execution_skipped is False


def test_compute_scheduler_summary_from_rows():
    rows = [
        SimpleNamespace(status="success", duration_ms=1000, auto_absent_marked=5),
        SimpleNamespace(status="partial", duration_ms=2000, auto_absent_marked=3),
        SimpleNamespace(status="failed", duration_ms=3000, auto_absent_marked=0),
        SimpleNamespace(status="success", duration_ms=4000, auto_absent_marked=2),
    ]
    summary = auto_absent_service.compute_scheduler_summary_from_rows(rows)
    assert summary["runs"] == 4
    assert summary["success_runs"] == 2
    assert summary["partial_runs"] == 1
    assert summary["failed_runs"] == 1
    assert summary["avg_duration_ms"] == 2500
    assert summary["avg_auto_absent_marked"] == 2
    assert summary["success_rate_pct"] == 50.0
