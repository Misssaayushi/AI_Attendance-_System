# Step 2: API Service Layer Alignment

## 🎯 Objective
Fix the Frontend's `api.js` service layer to call the **correct Backend endpoints** with the **correct request/response shapes**, replacing all non-existent endpoint calls.

---

## 📊 Current Mismatch Analysis

### Frontend `api.js` (Current — ❌ Broken)
```javascript
export const registerStudent = (data) => api.post('/api/v1/students/register', data);
export const getAttendanceLogs = () => api.get('/api/v1/attendance/logs');
export const getDashboardStats = () => api.get('/api/v1/attendance/stats');
export const getAttendanceRecords = (filters) => api.get('/api/v1/attendance/records', { params: filters });
```

### Backend Routes (Actual — ✅ Working)
| Frontend Calls | Backend Has | Status |
|---|---|---|
| `POST /api/v1/students/register` | `POST /api/v1/students/` | ❌ Wrong path |
| `GET /api/v1/attendance/logs` | Does NOT exist | ❌ No endpoint |
| `GET /api/v1/attendance/stats` | `GET /api/v1/dashboard/summary` | ❌ Wrong path |
| `GET /api/v1/attendance/records` | `GET /api/v1/attendance/` | ❌ Wrong path |

---

## 📝 Implementation Tasks

### Task 2.1 — Rewrite `src/services/api.js`

Replace all API functions with correctly mapped calls:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor (from Step 1)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (from Step 1)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// =================== AUTH ===================
export const loginAdmin = (username, password) =>
  api.post('/api/v1/auth/login', { username, password });

export const getMe = () => api.get('/api/v1/auth/me');

export const logoutAdmin = () => api.post('/api/v1/auth/logout');

// =================== STUDENTS ===================
export const listStudents = (params = {}) =>
  api.get('/api/v1/students/', { params });

export const getStudent = (studentId) =>
  api.get(`/api/v1/students/${studentId}`);

export const createStudent = (studentData) =>
  api.post('/api/v1/students/', studentData);

export const updateStudent = (studentId, studentData) =>
  api.put(`/api/v1/students/${studentId}`, studentData);

export const deleteStudent = (studentId) =>
  api.delete(`/api/v1/students/${studentId}`);

// =================== ATTENDANCE ===================
export const markAttendance = (payload) =>
  api.post('/api/v1/attendance/mark', payload);

export const listAttendance = (params = {}) =>
  api.get('/api/v1/attendance/', { params });

export const getAttendanceById = (attendanceId) =>
  api.get(`/api/v1/attendance/${attendanceId}`);

export const getStudentAttendance = (studentId, params = {}) =>
  api.get(`/api/v1/attendance/student/${studentId}`, { params });

export const getDailySummary = (params = {}) =>
  api.get('/api/v1/attendance/summary/daily', { params });

// =================== DASHBOARD ===================
export const getDashboardSummary = (params = {}) =>
  api.get('/api/v1/dashboard/summary', { params });

export const getDailyStats = (params = {}) =>
  api.get('/api/v1/dashboard/stats/daily', { params });

export const getMonthlyStats = (params = {}) =>
  api.get('/api/v1/dashboard/stats/monthly', { params });

export const getDepartmentStats = (params = {}) =>
  api.get('/api/v1/dashboard/stats/department', { params });

export const getWeeklyTrend = (params = {}) =>
  api.get('/api/v1/dashboard/graphs/weekly', { params });

export const getMonthlyTrend = (params = {}) =>
  api.get('/api/v1/dashboard/graphs/monthly', { params });

export const getDepartmentComparison = (params = {}) =>
  api.get('/api/v1/dashboard/graphs/department', { params });

// =================== EXPORTS ===================
export const getExportPreview = (params = {}) =>
  api.get('/api/v1/attendance/export/preview', { params });

export const exportMonthlyWorkbook = (params) =>
  api.post('/api/v1/attendance/export/monthly', null, { params });

// =================== DIAGNOSTICS ===================
export const getBackendReadiness = () =>
  api.get('/api/v1/diagnostics/readiness');

export const getHealthStatus = () =>
  api.get('/api/v1/health/');

export default api;
```

---

### Task 2.2 — Create `.env` File for Frontend

**File**: `frontend/Frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

> This allows easy environment switching (dev/staging/prod) without code changes.

---

### Task 2.3 — Verify Backend Response Wrapper

The Backend uses a standardized response wrapper. All routes return:
```json
{
  "success": true,
  "message": "...",
  "data": { /* actual payload */ }
}
```

Frontend code must extract `response.data.data` (not `response.data`).

**Create a helper** at `src/services/apiHelpers.js`:

```javascript
/**
 * Extract the actual data payload from Backend's standardized response.
 * Backend always returns: { success: bool, message: string, data: any }
 */
export const extractData = (response) => {
  return response?.data?.data ?? response?.data;
};

/**
 * Extract error message from Backend error response.
 */
export const extractErrorMessage = (error) => {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    'An unexpected error occurred'
  );
};
```

---

### Task 2.4 — Backend Request Schema Reference

The frontend must send data matching these Backend Pydantic schemas:

#### `POST /api/v1/students/` — `StudentCreate`
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "user@example.com",
  "roll_number": "string (3-30 chars, alphanumeric)",
  "contact_number": "string (optional, 7-15 digits)",
  "department": "string",
  "course": "string",
  "year_batch": "string",
  "semester": 1,
  "section": "string (optional)",
  "gender": "string",
  "face_encoding": [128 floats] // optional
}
```

#### `POST /api/v1/attendance/mark` — `AttendanceMarkRequest`
```json
{
  "student_id": 1,
  "attendance_date": "2026-05-20",     // optional, defaults to today
  "attendance_time": "09:00:00",       // optional, defaults to now
  "status": "Present",                  // "Present" | "Absent" | "Late"
  "confidence_score": 0.92,             // optional, 0.0 to 1.0
  "source": "ai_recognition"            // optional, defaults to "ai_recognition"
}
```

---

## ✅ Verification Checklist
- [ ] All Frontend API calls use correct Backend endpoint paths
- [ ] `.env` file created with `VITE_API_BASE_URL`
- [ ] `extractData()` helper used in all page components
- [ ] Request payloads match Backend Pydantic schemas
- [ ] No 404 errors when Frontend calls Backend endpoints

---

## 📁 Files Changed
| File | Action |
|---|---|
| `src/services/api.js` | **REWRITE** — all endpoints corrected |
| `src/services/apiHelpers.js` | **NEW** — response/error extraction |
| `frontend/Frontend/.env` | **NEW** — API base URL config |
