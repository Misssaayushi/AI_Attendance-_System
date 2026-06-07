# Step 01 - Excel Automation Architecture

## Goal
Define a modular architecture for Excel automation that integrates cleanly with existing FastAPI services.

## Design
- Route Layer: exposes export/report endpoints
- Service Layer: orchestrates workbook creation/update
- Repository Layer: fetches attendance/student data from MySQL
- Export Engine Layer: OpenPyXL/Pandas utilities for workbook operations
- Validation Layer: schema and data integrity checks before write

## Components
- WorkbookManager
- SheetBuilder
- AttendanceWriter
- ReportAggregator
- ExportStorageManager

## Output
A clear module contract for each component and call flow from API to file output.
