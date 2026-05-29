"""Phase 6 Step 1-2: Excel automation architecture and workbook template design."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet


PRIMARY_SHEET_NAME = "Monthly_Attendance"
SUMMARY_SHEET_NAME = "Summary"
METADATA_SHEET_NAME = "Metadata"

STATIC_STUDENT_COLUMNS = [
    "Student ID",
    "Roll Number",
    "Student Name",
    "Department",
    "Course",
    "Year/Batch",
    "Semester",
    "Section",
]

STATUS_CANONICAL_MAP = {
    "P": "Present",
    "A": "Absent",
    "L": "Late",
    "PRESENT": "Present",
    "ABSENT": "Absent",
    "LATE": "Late",
}

STATUS_PRIORITY = {
    "Absent": 1,
    "Late": 2,
    "Present": 3,
}


@dataclass
class ExcelAutomationConfig:
    export_dir: str
    include_summary_sheet: bool = True
    include_metadata_sheet: bool = True


class SheetBuilder:
    """Builds workbook sheets using a stable monthly attendance template."""

    @staticmethod
    def day_headers(year: int, month: int) -> List[str]:
        total_days = monthrange(year, month)[1]
        return [f"{day:02d}" for day in range(1, total_days + 1)]

    @classmethod
    def build_primary_sheet(cls, workbook: Workbook, year: int, month: int) -> Worksheet:
        sheet = workbook.active
        sheet.title = PRIMARY_SHEET_NAME

        headers = STATIC_STUDENT_COLUMNS + cls.day_headers(year, month)
        for idx, header in enumerate(headers, start=1):
            sheet.cell(row=1, column=idx, value=header)
        return sheet

    @staticmethod
    def build_summary_sheet(workbook: Workbook) -> Worksheet:
        sheet = workbook.create_sheet(title=SUMMARY_SHEET_NAME)
        headers = ["Metric", "Value"]
        for idx, header in enumerate(headers, start=1):
            sheet.cell(row=1, column=idx, value=header)
        return sheet

    @staticmethod
    def build_metadata_sheet(workbook: Workbook, year: int, month: int) -> Worksheet:
        sheet = workbook.create_sheet(title=METADATA_SHEET_NAME)
        sheet.cell(row=1, column=1, value="Key")
        sheet.cell(row=1, column=2, value="Value")
        sheet.cell(row=2, column=1, value="report_month")
        sheet.cell(row=2, column=2, value=f"{year:04d}-{month:02d}")
        sheet.cell(row=3, column=1, value="generated_at_utc")
        sheet.cell(row=3, column=2, value=datetime.now(timezone.utc).isoformat())
        return sheet


class WorkbookManager:
    """Creates and persists attendance workbooks with a consistent naming strategy."""

    @staticmethod
    def monthly_filename(year: int, month: int) -> str:
        return f"attendance_{year:04d}_{month:02d}.xlsx"

    @classmethod
    def monthly_workbook_path(cls, *, year: int, month: int, config: ExcelAutomationConfig) -> Path:
        export_dir = Path(config.export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir / cls.monthly_filename(year, month)

    @classmethod
    def create_monthly_workbook(cls, *, year: int, month: int, config: ExcelAutomationConfig) -> Workbook:
        workbook = Workbook()
        SheetBuilder.build_primary_sheet(workbook, year=year, month=month)
        if config.include_summary_sheet:
            SheetBuilder.build_summary_sheet(workbook)
        if config.include_metadata_sheet:
            SheetBuilder.build_metadata_sheet(workbook, year=year, month=month)
        return workbook

    @classmethod
    def save_monthly_workbook(
        cls,
        workbook: Workbook,
        *,
        year: int,
        month: int,
        config: ExcelAutomationConfig,
    ) -> str:
        output_path = cls.monthly_workbook_path(year=year, month=month, config=config)
        workbook.save(output_path)
        return str(output_path)

    @classmethod
    def load_or_create_monthly_workbook(
        cls,
        *,
        year: int,
        month: int,
        config: ExcelAutomationConfig,
    ) -> Workbook:
        file_path = cls.monthly_workbook_path(year=year, month=month, config=config)
        if file_path.exists():
            return load_workbook(file_path)
        return cls.create_monthly_workbook(year=year, month=month, config=config)


class DateColumnManager:
    """Step 4: Dynamic date-column utilities for monthly attendance sheets."""

    @staticmethod
    def expected_day_headers(year: int, month: int) -> List[str]:
        return SheetBuilder.day_headers(year, month)

    @staticmethod
    def date_to_day_header(attendance_date: date, *, year: int, month: int) -> str:
        if attendance_date.year != year or attendance_date.month != month:
            raise ValueError("attendance_date does not belong to target workbook month")
        return f"{attendance_date.day:02d}"

    @classmethod
    def ensure_day_columns(cls, sheet: Worksheet, *, year: int, month: int) -> Dict[str, int]:
        """
        Ensures all valid day headers for the month exist in row-1 and returns
        a day->column_index map (1-based). Existing headers are reused.
        """
        expected_days = cls.expected_day_headers(year, month)
        existing_map = RowColumnMapper.header_index_map(sheet)

        for day in expected_days:
            if day not in existing_map:
                next_col = sheet.max_column + 1
                sheet.cell(row=1, column=next_col, value=day)
                existing_map[day] = next_col

        # Normalize order by rewriting day columns contiguously after static columns.
        first_day_col = len(STATIC_STUDENT_COLUMNS) + 1
        for offset, day in enumerate(expected_days):
            target_col = first_day_col + offset
            sheet.cell(row=1, column=target_col, value=day)

        return {day: first_day_col + idx for idx, day in enumerate(expected_days)}

    @classmethod
    def resolve_date_column(cls, sheet: Worksheet, attendance_date: date, *, year: int, month: int) -> int:
        day_header = cls.date_to_day_header(attendance_date, year=year, month=month)
        day_map = cls.ensure_day_columns(sheet, year=year, month=month)
        return day_map[day_header]


class RowColumnMapper:
    """Step 3: Deterministic row/column mapping for attendance sheet writes."""

    @staticmethod
    def header_index_map(sheet: Worksheet) -> Dict[str, int]:
        mapping: Dict[str, int] = {}
        for col in range(1, sheet.max_column + 1):
            header = sheet.cell(row=1, column=col).value
            if header is None:
                continue
            mapping[str(header)] = col
        return mapping

    @classmethod
    def student_row_map(cls, sheet: Worksheet, *, student_key_header: str = "Student ID") -> Dict[str, int]:
        headers = cls.header_index_map(sheet)
        if student_key_header not in headers:
            raise ValueError(f"Missing required student key column: {student_key_header}")

        key_col = headers[student_key_header]
        row_map: Dict[str, int] = {}
        for row in range(2, sheet.max_row + 1):
            value = sheet.cell(row=row, column=key_col).value
            if value is None:
                continue
            row_map[str(value)] = row
        return row_map

    @staticmethod
    def next_available_student_row(sheet: Worksheet) -> int:
        return max(2, sheet.max_row + 1)


class AttendanceWriter:
    """Step 5: Writes attendance into workbook with deterministic mapping and conflict rules."""

    @staticmethod
    def canonicalize_status(value: str) -> str:
        key = str(value).strip().upper()
        if key not in STATUS_CANONICAL_MAP:
            raise ValueError(f"Unsupported attendance status: {value}")
        return STATUS_CANONICAL_MAP[key]

    @staticmethod
    def should_overwrite(existing_status: str | None, new_status: str) -> bool:
        if not existing_status:
            return True
        existing = AttendanceWriter.canonicalize_status(existing_status)
        incoming = AttendanceWriter.canonicalize_status(new_status)
        return STATUS_PRIORITY[incoming] >= STATUS_PRIORITY[existing]

    @staticmethod
    def write_student_metadata(sheet: Worksheet, row_idx: int, student: dict) -> None:
        headers = RowColumnMapper.header_index_map(sheet)
        sheet.cell(row=row_idx, column=headers["Student ID"], value=student.get("student_id"))
        sheet.cell(row=row_idx, column=headers["Roll Number"], value=student.get("roll_number"))
        sheet.cell(row=row_idx, column=headers["Student Name"], value=student.get("student_name"))
        sheet.cell(row=row_idx, column=headers["Department"], value=student.get("department"))
        sheet.cell(row=row_idx, column=headers["Course"], value=student.get("course"))
        sheet.cell(row=row_idx, column=headers["Year/Batch"], value=student.get("year_batch"))
        sheet.cell(row=row_idx, column=headers["Semester"], value=student.get("semester"))
        sheet.cell(row=row_idx, column=headers["Section"], value=student.get("section"))

    @classmethod
    def ensure_student_row(cls, *, sheet: Worksheet, student: dict) -> int:
        student_key = str(student["student_id"])
        row_map = RowColumnMapper.student_row_map(sheet, student_key_header="Student ID")
        if student_key in row_map:
            return row_map[student_key]
        row_idx = RowColumnMapper.next_available_student_row(sheet)
        cls.write_student_metadata(sheet, row_idx, student)
        return row_idx

    @classmethod
    def ensure_student_row_with_cache(
        cls,
        *,
        sheet: Worksheet,
        student: dict,
        row_map: Dict[str, int] | None = None,
    ) -> int:
        if row_map is None:
            return cls.ensure_student_row(sheet=sheet, student=student)

        student_key = str(student["student_id"])
        if student_key in row_map:
            return row_map[student_key]

        row_idx = RowColumnMapper.next_available_student_row(sheet)
        cls.write_student_metadata(sheet, row_idx, student)
        row_map[student_key] = row_idx
        return row_idx

    @classmethod
    def upsert_attendance_cell(
        cls,
        *,
        sheet: Worksheet,
        year: int,
        month: int,
        student: dict,
        attendance_date: date,
        status: str,
        row_map: Dict[str, int] | None = None,
        day_column_map: Dict[str, int] | None = None,
    ) -> dict:
        row_idx = cls.ensure_student_row_with_cache(sheet=sheet, student=student, row_map=row_map)
        day_header = DateColumnManager.date_to_day_header(attendance_date, year=year, month=month)
        if day_column_map is None:
            col_idx = DateColumnManager.resolve_date_column(sheet, attendance_date, year=year, month=month)
        else:
            col_idx = day_column_map[day_header]
        new_status = cls.canonicalize_status(status)
        existing_status = sheet.cell(row=row_idx, column=col_idx).value

        if cls.should_overwrite(existing_status, new_status):
            sheet.cell(row=row_idx, column=col_idx, value=new_status)
            action = "updated" if existing_status else "created"
        else:
            action = "skipped"

        return {
            "action": action,
            "row": row_idx,
            "column": col_idx,
            "existing_status": existing_status,
            "new_status": new_status,
        }
