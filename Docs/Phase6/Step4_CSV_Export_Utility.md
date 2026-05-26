# Step 4: CSV Export Utility

## Goal
Establish a client-side exporter that compiles active, filtered log records into a downloadable comma-separated values (CSV) file, ready for presentation reviews.

## Tasks
- [x] Write `handleExportCSV` function that structures headers and matches rows from the active filtered records state.
- [x] Encode the parsed data stream into URI characters.
- [x] Create a hidden `<a>` download element dynamically, set the appropriate file download name (`attendance_records_[date].csv`), trigger a mock click event, and cleanup.

## Files Affected
- `src/pages/Records.jsx`
