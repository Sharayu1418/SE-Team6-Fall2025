/**
 * Axios API client with session authentication.
 * 
 * Configured to:
 * - Include credentials (session cookies)
 * - Automatically attach CSRF tokens to requests
 * - Proxy through Vite dev server to Django backend
 */

import axios from 'axios';

// Helper to get CSRF token from cookie
function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Ensure CSRF cookie is set on app load
let csrfInitialized = false;
export async function initCsrf() {
  if (!csrfInitialized) {
    try {
      await api.get('/csrf/');
      csrfInitialized = true;
    } catch (e) {
      console.warn('Failed to initialize CSRF:', e);
    }
  }
}

// Initialize CSRF on module load
initCsrf();

// Add CSRF token to all requests
api.interceptors.request.use(
  (config) => {
    // For POST/PUT/PATCH/DELETE requests, add CSRF token
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())) {
      const token = getCsrfToken();
      if (token) {
        config.headers['X-CSRFToken'] = token;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

