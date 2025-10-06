import axios from 'axios';

// Dynamic API URL detection for mobile access
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // Use environment variable if available, otherwise localhost
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  // Fallback for server-side rendering
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

// Debug logging
if (typeof window !== 'undefined') {
  console.log('Frontend API Configuration:');
  console.log('- API_BASE_URL:', API_BASE_URL);
  console.log('- NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true,  // Enable credentials for CORS
  timeout: 30000,  // 30 second timeout
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  console.log('API Request:', config.url, 'Token:', token ? 'Present' : 'Missing');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Success:', response.config.url, response.status);
    return response;
  },
  (error) => {
    // Log error details for debugging
    console.error('API Error Details:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      data: error.response?.data,
      headers: error.config?.headers
    });
    
    if (error.response?.status === 401) {
      console.log('401 Unauthorized - clearing tokens and redirecting');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export { apiClient };
export default apiClient;