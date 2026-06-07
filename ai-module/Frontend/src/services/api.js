import axios from 'axios';

// Placeholder for Axios instance configuration
const api = axios.create({
  baseURL: 'http://localhost:8000', // Assuming FastAPI default port
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
