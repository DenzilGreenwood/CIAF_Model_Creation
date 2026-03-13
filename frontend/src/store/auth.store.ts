import { create } from 'zustand';
import { User, UserRole } from '@/types';

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  userRole: UserRole | null;

  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string) => void;
  setAuthenticated: (authenticated: boolean) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
  hasPermission: (requiredRole: UserRole | UserRole[]) => boolean;

  // Persistence
  hydrate: () => void;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  userRole: null,

  setUser: (user) => {
    set({ user, userRole: user?.role ?? null });
    if (user) {
      localStorage.setItem('ciaf_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('ciaf_user');
    }
  },

  setToken: (token) => {
    set({ token });
    localStorage.setItem('ciaf_jwt_token', token);
  },

  setAuthenticated: (authenticated) => {
    set({ isAuthenticated: authenticated });
  },

  login: (user, token) => {
    set({ user, token, isAuthenticated: true, userRole: user.role });
    localStorage.setItem('ciaf_user', JSON.stringify(user));
    localStorage.setItem('ciaf_jwt_token', token);
  },

  logout: () => {
    set({ user: null, token: null, isAuthenticated: false, userRole: null });
    localStorage.removeItem('ciaf_user');
    localStorage.removeItem('ciaf_jwt_token');
  },

  hasPermission: (requiredRole) => {
    const { userRole } = get();
    if (!userRole) return false;

    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    const roleHierarchy: Record<UserRole, number> = {
      'admin': 3,
      'analyst': 2,
      'auditor': 1,
      'viewer': 0,
    };

    const userLevel = roleHierarchy[userRole];
    const requiredLevel = Math.max(...roles.map(r => roleHierarchy[r]));

    return userLevel >= requiredLevel;
  },

  hydrate: () => {
    const storedUser = localStorage.getItem('ciaf_user');
    const storedToken = localStorage.getItem('ciaf_jwt_token');

    if (storedUser && storedToken) {
      const user = JSON.parse(storedUser) as User;
      set({
        user,
        token: storedToken,
        isAuthenticated: true,
        userRole: user.role,
      });
    }
  },
}));
