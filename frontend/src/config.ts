// API Configuration
// For local development without Docker, use localhost:8000
// For Docker/Production, this can be overridden by environment variables
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_URL = `${API_BASE_URL}/api`;
