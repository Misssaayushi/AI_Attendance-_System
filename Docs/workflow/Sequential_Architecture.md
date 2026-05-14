# Sequential System Pipeline Architecture

This document presents the complete system workflow using the sequential pipeline architecture style.

---

## Phase 1: Environment & Setup
```text
Requirement Analysis (Libraries, Hardware)
 |
 ↓
Virtual Environment Creation (Python venv)
 |
 ↓
Dependency Installation (OpenCV, Dlib, face_recognition)
 |
 ↓
Directory Scaffolding (ai_module, backend, frontend)
 |
 ↓
Configuration Setup (config.py, .env)
 |
 ↓
Setup Validation (Verify via test_scripts.py)
 |
 ↓
Setup Complete
```

---

## Phase 2: Face Detection & Quality Validation
```text
Webcam Initialization (OpenCV VideoCapture)
 |
 ↓
Frame Acquisition (Continuous stream loop)
 |
 ↓
Face Detection (HOG / Haar Cascades)
 |
 ↓
Image Pre-processing (Grayscale, Normalization)
 |
 ↓
Quality Validation (Blur, Size, Lighting checks)
 |
 ↓
User Feedback (Real-time UI/Console alerts)
 |
 ↓
Quality Check Passed
```

---

## Phase 3: Student Registration & Encoding
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

---

## Phase 4: Real-Time Recognition
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

---

## Phase 5: Backend & Database Integration
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

---

## Phase 6: Frontend Dashboard & Analytics
```text
User Authentication (Secure Admin Login)
 |
 ↓
Dashboard Loading (Initialize React State)
 |
 ↓
API Data Fetching (Fetch Attendance Logs)
 |
 ↓
Real-time Feed Integration (Websocket/Stream)
 |
 ↓
Chart Rendering (Chart.js Visualization)
 |
 ↓
Search & Filter Logic (Date, Dept, Roll No)
 |
 ↓
Report Export Generation (CSV / PDF)
 |
 ↓
Dashboard Update Complete
```
