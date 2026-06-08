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
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
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

export const registerFace = (studentId, images) =>
  api.post(`/api/v1/students/${studentId}/register-face`, { images });

export const triggerEncoding = (studentId) =>
  api.post(`/api/v1/students/${studentId}/encode`);

// =================== ATTENDANCE ===================
export const markAttendance = (payload) =>
  api.post('/api/v1/attendance/mark', payload);

export const recognizeFrame = (payload) =>
  api.post('/api/v1/attendance/recognize-frame', payload);

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

// =================== CLASS TIMINGS ===================
export const listClassTimings = () =>
  api.get('/api/v1/class-timings/');

export const upsertClassTiming = (data) =>
  api.post('/api/v1/class-timings/', data);

export const deleteClassTiming = (timingId) =>
  api.delete(`/api/v1/class-timings/${timingId}`);

// =================== EXPORTS ===================
export const getExportPreview = (params = {}) =>
  api.get('/api/v1/attendance/export/preview', { params });

export const exportMonthlyWorkbook = (params) =>
  api.post('/api/v1/attendance/export/monthly', null, { params });

// =================== DIAGNOSTICS ===================
export const getBackendReadiness = () =>
  api.get('/api/v1/diagnostics/readiness');

export const getHealthStatus = () =>
  api.get('/api/v1/health');

export default api;
