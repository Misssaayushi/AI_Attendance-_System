# 🔗 Full-Stack Integration Plan — Frontend ↔ Backend ↔ AI Module

## 📌 Purpose
This document is the **master plan** for wiring together the three independent pillars of the AI Attendance System:

| Pillar | Stack | Location | Port |
|---|---|---|---|
| **Frontend** | React + Vite + TailwindCSS | `frontend/Frontend/` | `5173` |
| **Backend** | FastAPI + MySQL + SQLAlchemy | `backend/Backend/` | `8000` |
| **AI Module** | Python + OpenCV + face_recognition | `ai-module/AI_Module/` | N/A (local process) |

---

## 🏗️ Current State Analysis

### What Works Independently
- ✅ **Frontend**: Full UI with Dashboard, Register, Attendance, Records pages. Uses mock/hardcoded data.
- ✅ **Backend**: Complete FastAPI API with JWT auth, CRUD for students, attendance marking, dashboard analytics, Excel exports, email reports, auto-absent scheduler.
- ✅ **AI Module**: Face detection, recognition, encoding, real-time verification with webcam, API service with mock mode, Phase 7 optimization, Phase 8 error handling, Phase 9 advanced features.

### What's Missing (The Integration Gaps)

| # | Gap | Impact |
|---|---|---|
| 1 | Frontend `api.js` calls wrong/non-existent endpoints (`/register`, `/logs`, `/stats`, `/records`) | Frontend cannot communicate with Backend |
| 2 | Frontend has no JWT authentication flow | All protected Backend routes return 401 |
| 3 | Frontend Registration doesn't sync with AI Module's dataset folder | Student faces won't be in AI recognition database |
| 4 | Frontend Dashboard uses hardcoded mock stats | Dashboard shows fake data, not real DB stats |
| 5 | Frontend Records page uses `mockAttendanceRecords` array | No real attendance data displayed |
| 6 | Frontend Attendance page uses simulation buttons only | No real AI recognition integration |
| 7 | AI Module's `api_service.py` sends to `/api/v1/attendance/verify` but Backend has `/api/v1/attendance/mark` | AI attendance events rejected by Backend |
| 8 | AI Module sends `student_id` as string, Backend expects `int` | Type mismatch causes validation errors |
| 9 | AI Module confidence is 0-100 scale, Backend expects 0.0-1.0 | Confidence values rejected by Backend |
| 10 | No WebSocket/SSE for real-time attendance feed | No live updates on Dashboard |
| 11 | No face encoding sync between Frontend registration and AI Module | Registration is incomplete without AI encoding |
| 12 | Backend `attendance/mark` requires auth, but AI Module has no auth token | AI Module cannot mark attendance |

---

## 📋 Integration Steps

The integration is organized into **10 sequential steps**. Each step has its own detailed document.

| Step | Title | Scope | Priority |
|---|---|---|---|
| **1** | [Authentication Integration](Step_1_Authentication_Integration.md) | Frontend ↔ Backend | 🔴 Critical |
| **2** | [API Service Layer Alignment](Step_2_API_Service_Layer.md) | Frontend `api.js` ↔ Backend routes | 🔴 Critical |
| **3** | [Student Registration Pipeline](Step_3_Registration_Pipeline.md) | Frontend ↔ Backend ↔ AI Module | 🔴 Critical |
| **4** | [AI-to-Backend Attendance Bridge](Step_4_AI_Backend_Bridge.md) | AI Module ↔ Backend | 🔴 Critical |
| **5** | [Dashboard Live Data Integration](Step_5_Dashboard_Integration.md) | Frontend ↔ Backend Analytics APIs | 🟡 High |
| **6** | [Records Page Backend Integration](Step_6_Records_Integration.md) | Frontend ↔ Backend Attendance APIs | 🟡 High |
| **7** | [Real-Time Attendance Feed (WebSocket)](Step_7_Realtime_Feed.md) | Frontend ↔ Backend ↔ AI Module | 🟡 High |
| **8** | [Attendance Terminal AI Integration](Step_8_Attendance_Terminal.md) | Frontend ↔ AI Module (via Backend) | 🟠 Medium |
| **9** | [Error Handling & Resilience](Step_9_Error_Handling.md) | All three pillars | 🟠 Medium |
| **10** | [End-to-End Testing & Validation](Step_10_E2E_Testing.md) | Full system | 🟢 Final |

---

## 🔄 Integration Architecture

```
┌──────────────┐     HTTP/REST      ┌──────────────┐     MySQL      ┌──────────────┐
│              │ ←────────────────→ │              │ ←───────────→ │              │
│   Frontend   │   JWT Auth Token   │   Backend    │   SQLAlchemy   │   Database   │
│  (React)     │   Axios + Bearer   │  (FastAPI)   │   ORM Layer    │  (MySQL)     │
│  Port: 5173  │                    │  Port: 8000  │                │  Port: 3306  │
│              │                    │              │                │              │
└──────────────┘                    └──────┬───────┘                └──────────────┘
                                          │
                                          │ HTTP POST
                                          │ /api/v1/attendance/mark
                                          │ (AI→Backend API Call)
                                          │
                                   ┌──────┴───────┐
                                   │              │
                                   │  AI Module   │
                                   │  (Python)    │
                                   │  Webcam      │
                                   │              │
                                   └──────────────┘
```

---

## 🚀 Quick Start (After Integration)

```bash
# Terminal 1: Start Backend
cd backend/Backend && source venv/bin/activate && python run.py

# Terminal 2: Start Frontend
cd frontend/Frontend && npm run dev

# Terminal 3: Start AI Recognition
cd ai-module/AI_Module && source venv/bin/activate && python recognize_faces.py
```

---

## ⚠️ Prerequisites
1. MySQL database `ai_attendance_db` created and running
2. Backend `.env` file configured with DB credentials
3. AI Module `dataset/` folder populated with student face images
4. AI Module `encodings/encodings.pickle` generated via `encode_faces.py`
5. All three virtual environments set up with dependencies installed
