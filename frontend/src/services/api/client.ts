import axios from 'axios';

// API base URLs for different services
const DJANGO_API_BASE = 'http://localhost:8000/api';
const EA_SERVICE_BASE = 'http://localhost:8001';

// Django Backend API client (primary)
const api = axios.create({
  baseURL: DJANGO_API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// EA Service API client (secondary)
const eaServiceApi = axios.create({
  baseURL: EA_SERVICE_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token to requests (both services)
const addAuthInterceptor = (apiInstance: any) => {
  apiInstance.interceptors.request.use(
    (config: any) => {
      const tokens = localStorage.getItem('tokens');
      if (tokens) {
        const { access } = JSON.parse(tokens);
        config.headers.Authorization = `Bearer ${access}`;
      }
      return config;
    },
    (error: any) => {
      return Promise.reject(error);
    }
  );
};

// Response interceptor for token refresh (Django only)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const tokens = localStorage.getItem('tokens');
      if (tokens) {
        const { refresh } = JSON.parse(tokens);
        
        try {
          const response = await axios.post(`${DJANGO_API_BASE}/token/refresh/`, {
            refresh,
          });
          
          const newTokens = {
            access: response.data.access,
            refresh: refresh,
          };
          
          localStorage.setItem('tokens', JSON.stringify(newTokens));
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('tokens');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Add auth interceptors to both clients
addAuthInterceptor(api);
addAuthInterceptor(eaServiceApi);

export default api;
export { eaServiceApi, DJANGO_API_BASE, EA_SERVICE_BASE };
