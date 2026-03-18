import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

export interface User {
    user_id: string;
    display_name: string;
    email: string;
    roles: string[];
}

interface UserContextType {
    currentUser: User | null;
    availableUsers: User[];
    switchUser: (userId: string) => void;
    isLoading: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
    const context = useContext(UserContext);
    if (!context) throw new Error('useUser must be used within UserProvider');
    return context;
};

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [availableUsers, setAvailableUsers] = useState<User[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        apiClient.get(API_ENDPOINTS.AUTH.USERS)
            .then(res => {
                const data = res.data;
                setAvailableUsers(data);
                if (data.length > 0) setCurrentUser(data[0]);
                setIsLoading(false);
            })
            .catch(err => {
                console.error("❌ Failed to fetch users in UserContext:", err);
                setIsLoading(false);
            });
    }, []);

    const switchUser = (id: string) => {
        const u = availableUsers.find(x => x.user_id === id);
        if (u) setCurrentUser(u);
    };

    return (
        <UserContext.Provider value={{ currentUser, availableUsers, switchUser, isLoading }}>
            {children}
        </UserContext.Provider>
    );
};
