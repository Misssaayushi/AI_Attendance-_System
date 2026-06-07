# Step 06 - Monthly Workbook Generation Workflow

## Goal
Generate monthly attendance workbooks at scale from DB records.

## Workflow
- Input: target month/year, optional filters
- Fetch student roster + month attendance records
- Build workbook from template contract
- Populate all student rows and date statuses
- Compute aggregate metrics (present/absent/late)
- Persist file to export directory

## Naming and Versioning
- Canonical filename by month
- Optional version suffix for regenerated files

## Output
Complete monthly workbook generation process.
