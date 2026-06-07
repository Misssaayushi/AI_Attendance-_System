# AI Attendance System

## Project Summary
This project is a full-stack smart attendance platform that uses face recognition to register students, verify attendance, store records, and present attendance analytics through a web dashboard.

The workspace is organized around three main modules:

- `frontend/Frontend`: the React + Vite web application
- `backend/Backend`: the FastAPI + MySQL backend API
- `ai-module/AI_Module`: the Python computer-vision and face-recognition module

In addition to the runnable code, the repository also contains phase-wise implementation notes, integration docs, PDFs, reports, and some historical/supporting copies of module files inside other folders.

## What The System Does
- Registers a student with profile details and captured face images.
- Saves face samples into the AI dataset and generates encodings for recognition.
- Accepts live webcam frames from the frontend attendance terminal.
- Recognizes faces and marks attendance through backend APIs.
- Prevents duplicate attendance for the same student on the same day.
- Tracks attendance as `Present`, `Late`, or `Absent`.
- Supports class timing rules by department and semester.
- Generates attendance summaries, graphs, export previews, and monthly workbooks.
- Provides admin login, student management, records pages, diagnostics, and settings.
- Broadcasts real-time attendance events over WebSocket.
- Includes scheduler and email-reporting infrastructure for automation.

## High-Level Architecture
### 1. Frontend
The frontend is a React 19 application built with Vite, Tailwind CSS, Axios, and Chart.js. It provides:

- A public registration page for enrolling students
- A public attendance terminal that captures webcam frames and sends them to the backend
- Protected admin pages for dashboard, records, students, and settings
- WebSocket-ready real-time attendance UX
- Analytics cards, charts, filtering, search, and CSV export features

### 2. Backend
The backend is a FastAPI application with SQLAlchemy and MySQL. It:

- Boots from `backend/Backend/app/main.py`
- Tests the database connection at startup
- Initializes database tables
- Starts the scheduler lifecycle on startup
- Exposes versioned APIs under `/api/v1`
- Uses JWT auth for admin routes
- Uses an internal API key for AI-to-backend attendance verification
- Includes middleware for logging, security headers, and centralized error handling

Main backend route groups:

- `/auth`: admin login and token-based session checks
- `/health`: health/status endpoints
- `/students`: create, update, delete, list, register face images, trigger encoding
- `/attendance`: manual and AI-driven attendance handling, summaries, exports
- `/dashboard`: analytics summaries and graphs
- `/diagnostics`: readiness, runtime metrics, and stability snapshots
- `/class-timings`: attendance-rule configuration by department/semester
- `/ws/attendance`: live attendance event stream

### 3. AI Module
The AI module is a Python/OpenCV/`face_recognition` pipeline that handles:

- Dataset-based face sample storage
- Face encoding generation
- Live face recognition
- Confidence scoring and attendance verification
- API transmission to the backend
- Retry logic, failed-event replay, diagnostics, and optimization helpers

Important AI scripts:

- `ai-module/AI_Module/register_face.py`: registration-side face capture workflow
- `ai-module/AI_Module/encode_faces.py`: encoding generation
- `ai-module/AI_Module/recognize_faces.py`: real-time recognition loop
- `ai-module/AI_Module/api_service.py`: backend API bridge
- `ai-module/AI_Module/optimization.py`: performance and caching helpers

## Main User Flows
### Student Registration Flow
1. A user opens the public registration page.
2. The frontend captures one or more face images through the webcam component.
3. The frontend submits student details to the backend.
4. The backend creates the student record in MySQL.
5. The frontend uploads captured face images to `/students/{id}/register-face`.
6. The backend saves those images into the AI dataset directory.
7. The frontend triggers `/students/{id}/encode`.
8. The backend runs the AI encoding script and stores the generated encoding back in the database.

### Attendance Flow
1. A user opens the public attendance terminal.
2. The frontend periodically sends webcam frames to `/api/v1/attendance/recognize-frame`.
3. The backend decodes the frame and compares it against dataset images and/or cached encodings.
4. If a valid match is found, attendance is marked.
5. Duplicate or cooldown cases are handled gracefully.
6. Attendance events are broadcast over WebSocket for real-time UI updates.

### Admin Flow
Authenticated admins can:

- View dashboard metrics and attendance graphs
- Search and filter attendance records
- Export attendance data
- Edit and delete students
- Configure class timing rules
- Access diagnostics endpoints

## Data Model Summary
Core backend models include:

- `Student`: personal details, academic fields, and stored face encoding
- `Attendance`: one attendance record per student per date with duplicate prevention
- `ClassTiming`: rule-based cutoffs for present/late handling
- `EmailDelivery`: tracking for automated report delivery attempts
- `Admin`: authenticated admin account model
- `SchedulerExecution`: scheduler history/audit tracking

## Important Features Present In Code
- Public student creation flow without admin auth
- Admin-protected management and analytics pages
- Internal API-key protected AI attendance verification
- MySQL persistence through SQLAlchemy
- Attendance uniqueness enforced at database level
- Daily/monthly analytics endpoints
- Diagnostics and monitoring endpoints
- Excel and workbook export services
- Scheduler setup for auto-absent and automation workflows
- Email-reporting service layer and attachment orchestration

## Repository Layout
```text
AI-Attendance System/
├── frontend/
│   ├── Frontend/                # Main React app
│   └── Docs/                    # Frontend phase docs and summaries
├── backend/
│   ├── Backend/                 # Main FastAPI app
│   ├── Docs/                    # Backend docs and summaries
│   └── AI_Module/               # Supporting/related files
├── ai-module/
│   ├── AI_Module/               # Main AI/ML code
│   ├── Docs/                    # AI planning, workflow, and reports
│   ├── Backend/                 # Supporting backend copy/reference
│   └── Frontend/                # Supporting frontend copy/reference
├── Integration/                 # Cross-module integration plans
├── run_frontend.sh              # Starts the frontend app
├── run_backend.sh               # Starts the backend app
└── run_ai.sh                    # Starts the AI module placeholder script
```

## Tech Stack
### Frontend
- React 19
- Vite
- Tailwind CSS 4
- Axios
- Chart.js
- React Router
- Lucide React

### Backend
- FastAPI
- SQLAlchemy
- MySQL Connector
- APScheduler
- OpenPyXL
- Pandas
- JWT auth utilities
- Uvicorn

### AI Module
- Python
- OpenCV
- `face_recognition`
- NumPy
- Requests

## How To Run
### Frontend
```bash
./run_frontend.sh
```

This runs:

```bash
cd frontend/Frontend
npm run dev
```

### Backend
```bash
./run_backend.sh
```

This runs:

```bash
cd backend/Backend
source venv/bin/activate
python run.py
```

### AI Module
```bash
./run_ai.sh
```

At the moment, this runs:

```bash
cd ai-module/AI_Module
source venv/bin/activate
python demo.py
```

`demo.py` is currently only a placeholder print script. The actual AI workflows live in:

- `ai-module/AI_Module/register_face.py`
- `ai-module/AI_Module/encode_faces.py`
- `ai-module/AI_Module/recognize_faces.py`

## Current Practical Notes
- The frontend expects the backend at `http://localhost:8000` unless `VITE_API_BASE_URL` is overridden.
- The backend expects a MySQL database and environment variables for DB, auth, scheduler, analytics, and email settings.
- The backend also references the AI module dataset and encoding paths through config.
- The workspace contains implementation docs and module copies in addition to the primary runnable apps, so the main folders to focus on are `frontend/Frontend`, `backend/Backend`, and `ai-module/AI_Module`.

## Overall Assessment
This is not just a prototype UI. The codebase already includes a fairly complete end-to-end attendance system with:

- registration
- face dataset capture
- encoding generation
- recognition-driven attendance marking
- admin analytics
- export/reporting infrastructure
- scheduling and diagnostics support

The strongest architectural theme of the project is the separation between the web UI, the API/business layer, and the AI recognition engine, with the backend acting as the integration hub between them.
