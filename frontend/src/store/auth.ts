import { create } from 'zustand';
import api from '@/lib/api';

interface User {
    id: string;
    nickname: string;
    cash_krw: number;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    login: (token: string, nickname: string) => Promise<void>;
    logout: () => void;
    fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
    isLoading: false,
    login: async (token: string, nickname: string) => {
        localStorage.setItem('token', token);
        set({ token });
        await get().fetchUser();
    },
    logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null });
    },
    fetchUser: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get('/auth/me');
            set({ user: response.data, isLoading: false });
        } catch (error) {
            console.error("Failed to fetch user", error);
            localStorage.removeItem('token');
            set({ user: null, token: null, isLoading: false });
        }
    },
}));
