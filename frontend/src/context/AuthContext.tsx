import React, { createContext, useState, useContext, useEffect } from 'react';
import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

// Define available roles from BQS_Prototype
export type UserRole = 'GH' | 'PH' | 'SH' | 'SA' | 'SP' | 'PSH' | 'BM' | 'SL' | 'LEGAL' | 'FINANCE' | 'LL';

// Define the User shape
export interface User {
    id: string;
    email: string;
    name: string;
    role: UserRole;
    displayRole: string;
}

// Define the RealUser from Backend
export interface RealUser {
    user_id: string;
    display_name: string;
    email: string;
    roles: string[];
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string) => Promise<void>;
    devLogin: (role: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    availableUsers: RealUser[];
    isLoadingUsers: boolean;
    authFetch: (url: string, options?: RequestInit) => Promise<Response>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Conditionally active simulated login
const DEV_MODE = import.meta.env.VITE_DEV_MODE === 'true';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // 1. Initialize from LocalStorage or Default
    const [user, setUser] = useState<User | null>(() => {
        const saved = localStorage.getItem('bqs_user');
        return saved ? JSON.parse(saved) : null;
    });

    const [token, setToken] = useState<string | null>(() => {
        return localStorage.getItem('bqs_token');
    });

    const [availableUsers, setAvailableUsers] = useState<RealUser[]>([]);
    const [isLoadingUsers, setIsLoadingUsers] = useState(true);

    // Fetch real users from backend on mount
    useEffect(() => {
        const fetchUsers = async () => {
            try {
                setIsLoadingUsers(true);
                const response = await apiClient.get(API_ENDPOINTS.AUTH.USERS);
                if (response.status === 200) {
                    setAvailableUsers(response.data);
                }
            } catch (error) {
                console.error("❌ Failed to fetch users in AuthContext:", error);
            } finally {
                setIsLoadingUsers(false);
            }
        };

        fetchUsers();
    }, []);

    const login = async (email: string) => {
        // Step 1 — Simulate an Azure SSO login interaction using the selected user's email
        const simulatedSsoToken = `mock_azure_token_${email}`;

        const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, { sso_token: simulatedSsoToken });

        if (response.status !== 200) {
            throw new Error(`SSO Login failed (${response.status}): ${response.data.detail || 'User not found or inactive'}`);
        }

        const { access_token: newToken } = response.data;
        setToken(newToken);
        localStorage.setItem('bqs_token', newToken);

        // Step 2 — fetch full user profile so we get real user_id + roles
        const meResponse = await apiClient.get(API_ENDPOINTS.AUTH.ME, {
            headers: { Authorization: `Bearer ${newToken}` },
        });

        if (meResponse.status !== 200) {
            throw new Error('Failed to fetch user profile after login.');
        }

        const meData = meResponse.data;
        const primaryRole = (meData.roles?.[0] || 'SP') as UserRole;
        const ROLE_LABELS: Record<string, string> = {
            GH: 'Global Head', PH: 'Practice Head', SH: 'Sales Head',
            SA: 'Solution Architect', SP: 'Sales Person', PSH: 'Presales Head',
            BM: 'Bid Manager', SL: 'Sales Lead', LEGAL: 'Legal Lead', FINANCE: 'Finance Controller', LL: 'Legal Lead'
        };

        const newUser: User = {
            id: meData.user_id,
            email: meData.email,
            name: meData.display_name,
            role: primaryRole,
            displayRole: ROLE_LABELS[primaryRole] ?? primaryRole,
        };

        console.log(`🔒 Logged in as: ${newUser.name} (${newUser.role}) via SSO JWT`);
        setUser(newUser);
        localStorage.setItem('bqs_user', JSON.stringify(newUser));
    };

    const devLogin = async (role: string) => {
        // Step 1 — Call the dev-login endpoint
        const response = await apiClient.post('/api/auth/dev-login', { role_code: role });

        if (response.status !== 200) {
            throw new Error(`Dev Login failed (${response.status}): ${response.data.detail || 'User not found or inactive'}`);
        }

        const { access_token: newToken } = response.data;
        setToken(newToken);
        localStorage.setItem('bqs_token', newToken);

        // Step 2 — fetch full user profile
        const meResponse = await apiClient.get(API_ENDPOINTS.AUTH.ME, {
            headers: { Authorization: `Bearer ${newToken}` },
        });

        if (meResponse.status !== 200) {
            throw new Error('Failed to fetch user profile after login.');
        }

        const meData = meResponse.data;
        const primaryRole = (meData.roles?.[0] || role) as UserRole;
        const ROLE_LABELS: Record<string, string> = {
            GH: 'Global Head', PH: 'Practice Head', SH: 'Sales Head',
            SA: 'Solution Architect', SP: 'Sales Person', PSH: 'Presales Head',
            LEGAL: 'Legal Lead', FINANCE: 'Finance Controller', LL: 'Legal Lead'
        };

        const newUser: User = {
            id: meData.user_id,
            email: meData.email,
            name: meData.display_name,
            role: primaryRole,
            displayRole: ROLE_LABELS[primaryRole] ?? primaryRole,
        };

        console.log(`🔒 Dev logged in as: ${newUser.name} (${newUser.role}) via Dev JWT`);
        setUser(newUser);
        localStorage.setItem('bqs_user', JSON.stringify(newUser));
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('bqs_user');
        localStorage.removeItem('bqs_token');
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    };

    // Wrapper for fetch that injects the JWT token and handles 401s (Backward Compatibility)
    const authFetch = async (url: string, options: RequestInit = {}) => {
        const headers = new Headers(options.headers || {});
        const activeToken = token || localStorage.getItem('bqs_token');
        if (activeToken) {
            headers.set('Authorization', `Bearer ${activeToken}`);
        }

        try {
            const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
            const finalUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;

            const response = await fetch(finalUrl, {
                ...options,
                headers
            });

            if (response.status === 401) {
                console.error("⛔ Unauthorized (401). Logging out...");
                if (!DEV_MODE || activeToken) {
                    logout();
                }
            }

            return response;
        } catch (error) {
            console.error("🌐 Network Error in authFetch:", error);
            throw error;
        }
    };

    return (
        <AuthContext.Provider value={{ 
            user, 
            token, 
            login, 
            devLogin, 
            logout, 
            isAuthenticated: !!user, 
            availableUsers, 
            isLoadingUsers,
            authFetch 
        }}>
            {children}
        </AuthContext.Provider>
    );
};

// Custom Hook
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
