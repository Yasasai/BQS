import React, { createContext, useContext, useState, ReactNode } from 'react';

export type UserRole = 'MANAGEMENT' | 'PRACTICE_HEAD' | 'SOLUTION_ARCHITECT';

interface User {
    id: string;
    name: string;
    email: string;
    role: UserRole;
}

interface UserContextType {
    currentUser: User;
    setCurrentUser: (user: User) => void;
    setRole: (role: UserRole) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error('useUser must be used within UserProvider');
    }
    return context;
};

interface UserProviderProps {
    children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
    // Default user - Practice Head who assigns and reviews
    const [currentUser, setCurrentUser] = useState<User>({
        id: '1',
        name: 'Bid Team User',
        email: 'user@inspiraenterprise.com',
        role: 'PRACTICE_HEAD' // Default role
    });

    const setRole = (role: UserRole) => {
        setCurrentUser(prev => ({ ...prev, role }));
    };

    return (
        <UserContext.Provider value={{ currentUser, setCurrentUser, setRole }}>
            {children}
        </UserContext.Provider>
    );
};
