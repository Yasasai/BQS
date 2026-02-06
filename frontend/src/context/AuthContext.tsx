import React, { createContext, useContext, useState, useEffect } from 'react';

// Define available roles from BQS_Prototype
export type UserRole = 'GH' | 'PH' | 'SH' | 'SA' | 'SP';

// Define the User shape
export interface User {
    id: string;
    email: string;
    name: string;
    role: UserRole;
    displayRole: string;
}

interface AuthContextType {
    user: User | null;
    login: (role: UserRole) => void;
    logout: () => void;
    isAuthenticated: boolean;
    availableRoles: { role: UserRole; label: string }[];
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// MOCK USERS for simulation
const MOCK_USERS: Record<UserRole, User> = {
    GH: { id: 'GH_001', email: 'global.head@company.com', name: 'Global Head (Gary)', role: 'GH', displayRole: 'Global Head' },
    PH: { id: 'PH_001', email: 'practice.head@company.com', name: 'Practice Head (Sarah)', role: 'PH', displayRole: 'Practice Head' },
    SH: { id: 'SH_001', email: 'sales.head@company.com', name: 'Sales Head (Sam)', role: 'SH', displayRole: 'Sales Head' },
    SA: { id: 'SA_JOHN', email: 'john.sa@example.com', name: 'John Architect', role: 'SA', displayRole: 'Solution Architect' },
    SP: { id: 'SP_JANE', email: 'jane.sp@example.com', name: 'Jane Presales', role: 'SP', displayRole: 'Sales Presales' },
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // 1. Initialize from LocalStorage or Default
    const [user, setUser] = useState<User | null>(() => {
        const saved = localStorage.getItem('bqs_user');
        return saved ? JSON.parse(saved) : MOCK_USERS.PH;
    });

    const login = (role: UserRole) => {
        const newUser = MOCK_USERS[role];
        console.log(`🔒 Logged in as: ${newUser.displayRole}`);
        setUser(newUser);
        localStorage.setItem('bqs_user', JSON.stringify(newUser));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('bqs_user');
    };

    const availableRoles: { role: UserRole; label: string }[] = [
        { role: 'GH', label: 'Global Head' },
        { role: 'PH', label: 'Practice Head' },
        { role: 'SH', label: 'Sales Head' },
        { role: 'SA', label: 'Solution Architect' },
        { role: 'SP', label: 'Sales Presales' },
    ];

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user, availableRoles }}>
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
