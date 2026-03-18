import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to inject the JWT token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('bqs_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle global errors (like 401 Unauthorized)
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            console.error("⛔ Unauthorized (401). Logging out...");
            // We can dispatch a custom event or rely on the AuthContext to handle this
            // For now, we clear the storage to force a re-login on next page load
            localStorage.removeItem('bqs_user');
            localStorage.removeItem('bqs_token');
            
            // Optional: Redirect to login if not in dev mode
            if (import.meta.env.VITE_DEV_MODE !== 'true') {
                window.location.href = '/';
            }
        }
        return Promise.reject(error);
    }
);

export default apiClient;
