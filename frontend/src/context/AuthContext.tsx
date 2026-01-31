import React, { createContext, useContext, useState, useEffect } from 'react';

// Define available roles
export type UserRole = 'PRACTICE_HEAD' | 'SOLUTION_ARCHITECT';

// Define the User shape
export interface User {
    id: string;
    email: string;
    name: string;
    role: UserRole;
}

interface AuthContextType {
    user: User | null;
    login: (role: UserRole) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// MOCK USERS for simulation
const MOCK_PH_USER: User = {
    id: 'PH_001',
    email: 'practice.head@company.com',
    name: 'Practice Head (Sarah)',
    role: 'PRACTICE_HEAD'
};

const MOCK_SA_USER: User = {
    id: 'SA_JOHN.SA',
    email: 'john.sa@example.com',
    name: 'John Architect',
    role: 'SOLUTION_ARCHITECT'
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // 1. Initialize from LocalStorage or Default
    const [user, setUser] = useState<User | null>(() => {
        const saved = localStorage.getItem('bqs_user');
        return saved ? JSON.parse(saved) : MOCK_PH_USER;
    });

    const login = (role: UserRole) => {
        let newUser: User;
        if (role === 'PRACTICE_HEAD') {
            newUser = MOCK_PH_USER;
            console.log("🔒 Logged in as: Practice Head");
        } else {
            newUser = MOCK_SA_USER;
            console.log("🔒 Logged in as: Solution Architect");
        }
        setUser(newUser);
        localStorage.setItem('bqs_user', JSON.stringify(newUser));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('bqs_user');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
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
