# Phase 5: Backend & Database Integration Workflow

## Description
Bridges the AI recognition engine with a persistent storage system to log attendance records.

## Sequential Pipeline Architecture
```text
API Endpoint Activation (Flask/FastAPI)
 |
 ↓
Request Reception (Student ID, Timestamp)
 |
 ↓
Database Lookup (MySQL Student Table)
 |
 ↓
Duplicate Check (Check if already marked today)
 |
 ↓
Attendance Logging (SQL INSERT Operation)
 |
 ↓
Excel Data Injection (update .xlsx via OpenPyXL)
 |
 ↓
Daily Summary Generation
 |
 ↓
Automated Email Dispatch (SMTP / Scheduler)
```

## Visual Flow (Technical)
```mermaid
graph TD
    A[Recognition Engine Triggers Match] --> B[Send Student ID to Flask API]
    B --> C[Verify Student in MySQL Database]
    C --> D{Already Marked Today?}
    D -- Yes --> E[Ignore / Show 'Already Marked']
    D -- No --> F[Insert Attendance Record with Timestamp]
    F --> G[Update Daily/Monthly Excel Sheets]
    G --> H[Check Closing Time via Scheduler]
    H --> I[Auto-Mark Absentees & Email Report]
    I --> J[End]
```
