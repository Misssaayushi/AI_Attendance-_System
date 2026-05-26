import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const registerStudent = (studentData) => api.post('/api/v1/students/register', studentData);
export const getAttendanceLogs = () => api.get('/api/v1/attendance/logs');
export const getDashboardStats = () => api.get('/api/v1/attendance/stats');
export const getAttendanceRecords = (filters) => api.get('/api/v1/attendance/records', { params: filters });

export default api;
