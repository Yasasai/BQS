import React, { createContext, useContext, useState, ReactNode } from 'react';

export type UserRole = 'management' | 'practice_head' | 'solution_architect';

interface User {
    id: string;
    name: string;
    email: string;
    role: UserRole;
}

interface UserContextType {
    currentUser: User;
    setCurrentUser: (user: User) => void;
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
        name: 'Practice Head',
        email: 'practice.head@inspiraenterprise.com',
        role: 'practice_head' // Practice Head - assigns SAs and reviews assessments
    });

    return (
        <UserContext.Provider value={{ currentUser, setCurrentUser }}>
            {children}
        </UserContext.Provider>
    );
};
