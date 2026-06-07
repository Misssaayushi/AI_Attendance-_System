# Phase 4: Real-Time Recognition Workflow

## Description
The core engine that identifies students from the live video feed by comparing their real-time encodings.

## Sequential Pipeline Architecture
```text
System Initialization (Load FaceDetector)
 |
 ↓
Encoding Retrieval (Load .pkl from encodings/)
 |
 ↓
Real-time Stream Start
 |
 ↓
Face Detection in Live Feed
 |
 ↓
Live 128D Encoding Generation
 |
 ↓
Distance Comparison (Euclidean Distance)
 |
 ↓
Match Verification (Confidence Thresholding)
 |
 ↓
Identification Overlay (Bounding Boxes, Name)
 |
 ↓
Attendance Trigger (Signal to Backend)
```

## Visual Flow (Technical)
```mermaid
graph TD
    A[Start Live Recognition Feed] --> B[Load Registered Encodings into RAM]
    B --> C[Process Video Frame]
    C --> D[Generate Live 128D Encoding]
    D --> E[Calculate Euclidean Distance]
    E --> F{Match Found within Threshold?}
    F -- Yes --> G[Identify Student & Calculate Confidence]
    F -- No --> H[Label as 'Unknown Person']
    G --> I[Render Bounding Box and Name Overlay]
    H --> I
    I --> J[Display FPS and Status]
    J --> C
```
