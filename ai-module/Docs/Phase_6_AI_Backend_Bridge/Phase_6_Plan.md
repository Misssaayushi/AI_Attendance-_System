# Phase 6: AI-Backend Communication Bridge - Implementation Plan

## Objective
Build the communication bridge that allows the AI recognition module to send verified attendance events to the FastAPI backend without breaking the real-time webcam pipeline.

Phase 6 does not create database tables, backend routes, or React UI features. It focuses only on the AI-side HTTP client, event payload structure, mock testing, and feedback shown in the OpenCV recognition overlay.

---

## Core Principle
The AI module remains the source of truth for:
- Student identity detected by face recognition.
- Verification timestamp.
- Confidence score.
- Final decision that attendance is ready to be transmitted.

The backend receives a finalized attendance event. If the backend is down or returns an error, the AI module must continue running and recognizing faces.

---

## Target Workflow
1. Face is recognized by `FaceRecognizer`.
2. Phase 5 verification confirms confidence, stability, and cooldown.
3. `api_service.py` builds an attendance payload.
4. Event is sent to `POST /api/v1/attendance/verify`.
5. Backend response is converted into a safe status message.
6. `recognize_faces.py` displays server feedback on the video feed.
7. Phase 5 cooldown prevents duplicate transmissions.

---

## Files To Create
- `ai_module/api_service.py`
- `ai_module/tests/test_integration.py`
- `Docs/Phase_6_AI_Backend_Bridge/Step_1_API_Config.md`
- `Docs/Phase_6_AI_Backend_Bridge/Step_2_API_Service_Layer.md`
- `Docs/Phase_6_AI_Backend_Bridge/Step_3_Mock_Mode.md`
- `Docs/Phase_6_AI_Backend_Bridge/Step_4_Recognition_Integration.md`
- `Docs/Phase_6_AI_Backend_Bridge/Step_5_Integration_Testing.md`

## Files To Modify Later
- `ai_module/config.py`
- `ai_module/recognize_faces.py`

---

## Ordered Phase Tasks

### Step 1 - API Configuration
Add centralized API settings to `config.py`, including backend base URL, attendance endpoint path, request timeout, retry count, and mock mode switch.

### Step 2 - API Service Layer
Create `api_service.py` with a reusable `AttendanceAPIService` class. This class owns payload creation, HTTP POST transmission, response parsing, logging, and graceful exception handling.

### Step 3 - Mock Mode
Add a mock mode path that returns predictable success or failure responses without requiring the FastAPI backend. This allows the AI-side recognition and verification loop to be tested independently.

### Step 4 - Recognition Loop Integration
Update `recognize_faces.py` so API transmission happens only after Phase 5 verification returns `verified=True`. Display API feedback in the OpenCV overlay.

### Step 5 - Integration Testing
Create `test_integration.py` to simulate successful backend responses, failed responses, timeouts, connection errors, and mock mode behavior.

---

## Completion Criteria
- Verified students generate exactly one transmission per cooldown window.
- Backend errors do not crash the webcam loop.
- Mock mode proves the AI-side flow without a live backend.
- Logs use the logger name `API_Connector`.
- API payloads use clear type hints.
- Recognition overlay can show messages such as `Attendance Logged`, `Server Error`, `Mock Success`, or `Retry Failed`.

