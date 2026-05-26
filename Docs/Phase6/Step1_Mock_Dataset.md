# Step 1: Mock Dataset Setup

## Goal
Establish a high-fidelity, comprehensive local database of attendance logs in `Records.jsx` to test search, multi-parameter filtering, sorting, and export capabilities.

## Tasks
- [x] Define a mock records array `mockAttendanceRecords` inside `src/pages/Records.jsx`.
- [x] Populated with 20+ entries containing:
  - `id`: Student ID / Roll number in the format `STU-2026-XXX`.
  - `name`: Student Name.
  - `date`: Attendance check-in date in `YYYY-MM-DD` format.
  - `time`: Check-in time (e.g. `09:01 AM`) or `---` if absent.
  - `department`: College branch (`CS`, `IT`, `ME`, `EE`).
  - `status`: Attendance status (`Present`, `Late`, `Absent`).

## Files Affected
- `src/pages/Records.jsx`
