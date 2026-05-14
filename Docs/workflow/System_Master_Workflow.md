# Overall System Master Workflow

## Description
This master flowchart illustrates the end-to-end journey from a student's first registration to the final automated attendance report.

## Master Workflow
```mermaid
graph TD
    subgraph Registration_Module
    R1[Open Registration] --> R2[Capture Samples]
    R2 --> R3[Generate Encodings]
    R3 --> R4[Save to Database]
    end

    subgraph Attendance_Module
    A1[Live Webcam Feed] --> A2[Detect & Recognize Face]
    A2 --> A3{Match Found?}
    A3 -- Yes --> A4[Verify Identity]
    A4 --> A5[Log to MySQL]
    A3 -- No --> A1
    end

    subgraph Backend_Automation
    B1[Log Entry] --> B2[Update Excel Sheet]
    B2 --> B3[Trigger Scheduler at 5:00 PM]
    B3 --> B4[Generate Absentee List]
    B4 --> B5[Email Report to Admin]
    end

    subgraph Admin_Dashboard
    D1[Admin Login] --> D2[View Real-Time Analytics]
    D2 --> D3[Manage Student Records]
    D3 --> D4[Download Reports]
    end

    Registration_Module --> Attendance_Module
    Attendance_Module --> Backend_Automation
    Backend_Automation --> Admin_Dashboard
```

## Workflow Summary
1.  **Registration**: One-time biometric data collection.
2.  **Recognition**: Daily automated identity verification.
3.  **Automation**: Background processing and report delivery.
4.  **Analytics**: Visual monitoring and data management.
