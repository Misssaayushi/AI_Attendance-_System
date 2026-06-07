from datetime import date

from app.exports.excel_automation import (
    AttendanceWriter,
    DateColumnManager,
    ExcelAutomationConfig,
    METADATA_SHEET_NAME,
    PRIMARY_SHEET_NAME,
    RowColumnMapper,
    STATIC_STUDENT_COLUMNS,
    SUMMARY_SHEET_NAME,
    WorkbookManager,
)


def test_monthly_filename():
    assert WorkbookManager.monthly_filename(2026, 5) == "attendance_2026_05.xlsx"


def test_workbook_template_contains_expected_sheets():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2026, month=5, config=config)
    assert PRIMARY_SHEET_NAME in wb.sheetnames
    assert SUMMARY_SHEET_NAME in wb.sheetnames
    assert METADATA_SHEET_NAME in wb.sheetnames


def test_primary_sheet_headers_for_31_day_month():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2026, month=5, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]

    expected_headers = STATIC_STUDENT_COLUMNS + [f"{d:02d}" for d in range(1, 32)]
    actual_headers = [sheet.cell(row=1, column=i + 1).value for i in range(len(expected_headers))]
    assert actual_headers == expected_headers


def test_primary_sheet_headers_for_leap_february():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2028, month=2, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]

    expected_headers = STATIC_STUDENT_COLUMNS + [f"{d:02d}" for d in range(1, 30)]
    actual_headers = [sheet.cell(row=1, column=i + 1).value for i in range(len(expected_headers))]
    assert actual_headers == expected_headers


def test_student_row_map_uses_student_id_column():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2026, month=5, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]

    header_map = RowColumnMapper.header_index_map(sheet)
    sid_col = header_map["Student ID"]
    sheet.cell(row=2, column=sid_col, value=101)
    sheet.cell(row=3, column=sid_col, value=205)

    row_map = RowColumnMapper.student_row_map(sheet, student_key_header="Student ID")
    assert row_map["101"] == 2
    assert row_map["205"] == 3


def test_resolve_date_column_for_valid_month_date():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2026, month=5, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]

    col = DateColumnManager.resolve_date_column(
        sheet,
        date(2026, 5, 21),
        year=2026,
        month=5,
    )
    expected = len(STATIC_STUDENT_COLUMNS) + 21
    assert col == expected


def test_resolve_date_column_rejects_cross_month_date():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2026, month=5, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]

    try:
        DateColumnManager.resolve_date_column(
            sheet,
            date(2026, 6, 1),
            year=2026,
            month=5,
        )
        assert False, "Expected ValueError for month mismatch"
    except ValueError:
        assert True


def test_ensure_student_row_creates_and_reuses_row():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2026, month=5, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]

    student = {
        "student_id": 5001,
        "roll_number": "ROLL5001",
        "student_name": "Test Student",
        "department": "CSE",
        "course": "B.Tech",
        "year_batch": "2026",
        "semester": 6,
        "section": "A",
    }
    row_1 = AttendanceWriter.ensure_student_row(sheet=sheet, student=student)
    row_2 = AttendanceWriter.ensure_student_row(sheet=sheet, student=student)

    assert row_1 == 2
    assert row_2 == 2


def test_attendance_writer_conflict_rule_priority():
    assert AttendanceWriter.should_overwrite("Absent", "Late") is True
    assert AttendanceWriter.should_overwrite("Present", "Absent") is False


def test_ensure_student_row_with_cache_updates_cache():
    config = ExcelAutomationConfig(export_dir=".")
    wb = WorkbookManager.create_monthly_workbook(year=2026, month=5, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]

    row_map = {}
    student = {
        "student_id": 7001,
        "roll_number": "ROLL7001",
        "student_name": "Cache Student",
        "department": "IT",
        "course": "B.Tech",
        "year_batch": "2026",
        "semester": 6,
        "section": "B",
    }
    row = AttendanceWriter.ensure_student_row_with_cache(sheet=sheet, student=student, row_map=row_map)
    assert row == 2
    assert row_map["7001"] == 2
