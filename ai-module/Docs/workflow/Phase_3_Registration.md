# Phase 3: Student Registration & Encoding Workflow

## Description
This phase handles the enrollment of new students by capturing multiple face samples and converting them into biometric signatures.

## Sequential Pipeline Architecture
```text
Terminal Input (Student ID, Name)
 |
 ↓
Webcam Stream Starts
 |
 ↓
Face Detection (reuse Phase 2 FaceDetector)
 |
 ↓
Quality Validation (blur, size, lighting)
 |
 ↓
Sample Capture (20 frames, timed intervals)
 |
 ↓
Image Storage (dataset/{student_id}/)
 |
 ↓
Encoding Generation (from saved images)
 |
 ↓
Encoding Storage (encodings/{student_id}.pkl)
 |
 ↓
Registration Complete
```

## Visual Flow (Technical)
```mermaid
graph TD
    A[Input Student Details: Name, Roll No] --> B[Capture N Face Samples]
    B --> C[Extract Face Region]
    C --> D[Generate 128D Encodings via Dlib]
    D --> E[Aggregate/Average Encodings for Accuracy]
    E --> F[Serialize Data using Pickle]
    F --> G[Save Encoding File to 'encodings/' folder]
    G --> H[End]
```
