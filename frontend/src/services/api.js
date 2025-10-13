import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
};

// Entries API
export const entriesAPI = {
  list: (params) => api.get('/entries', { params }),
  get: (id) => api.get(`/entries/${id}`),
  create: (data) => api.post('/entries', data),
  update: (id, data) => api.patch(`/entries/${id}`, data),
  delete: (id) => api.delete(`/entries/${id}`),
};

export default api;
