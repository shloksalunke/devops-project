import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
console.log('🔗 Configuring API Client with Base URL:', API_BASE_URL);

const client = axios.create({
  baseURL: API_BASE_URL,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('campusride_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData - let axios handle it
  if (!(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json';
  } else {
    // Remove Content-Type for FormData so axios adds multipart/form-data with boundary
    delete config.headers['Content-Type'];
    console.log('📤 FormData Request', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      dataIsFormData: config.data instanceof FormData,
    });
  }

  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('❌ API Error Response', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers,
      });
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('campusride_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default client;
