import axios from 'axios';

// API base URL - use relative path for production (Docker/Nginx), absolute for local dev
const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const authAPI = {
  // Get users count
  getUsersCount: () => api.get('/api/users/count'),

  // Register user
  register: (data) => {
    const formData = new FormData();
    formData.append('name', data.name);
    if (data.email) formData.append('email', data.email);
    formData.append('image', data.image);

    return api.post('/api/register', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Login user
  login: (data) => {
    const formData = new FormData();
    formData.append('image', data.image);
    formData.append('recognition_threshold', data.recognition_threshold || 0.6);
    formData.append('security_level', data.security_level || 3);

    return api.post('/api/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get user info
  getUser: (userId) => api.get(`/api/user/${userId}`),

  // Get login history
  getLoginHistory: (userId, limit = 20) =>
    api.get(`/api/user/${userId}/history`, { params: { limit } }),

  // Delete user
  deleteUser: (userId) => api.delete(`/api/user/${userId}`),

  // Health check
  healthCheck: () => api.get('/api/health'),
};

export default api;
