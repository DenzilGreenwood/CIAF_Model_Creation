import { create } from 'zustand';
import { User, UserRole } from '@/types';

interface AuthStore {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  userRole: UserRole | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string) => void;
  setRefreshToken: (token: string | null) => void;
  setAuthenticated: (authenticated: boolean) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  login: (user: User, token: string, refreshToken?: string) => void;
  logout: () => void;
  refreshAccessToken: (newToken: string) => void;
  hasPermission: (requiredRole: UserRole | UserRole[]) => boolean;
  clearError: () => void;

  // Persistence
  hydrate: () => void;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  userRole: null,
  isLoading: false,
  error: null,

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

  setRefreshToken: (refreshToken) => {
    set({ refreshToken });
    if (refreshToken) {
      localStorage.setItem('ciaf_refresh_token', refreshToken);
    } else {
      localStorage.removeItem('ciaf_refresh_token');
    }
  },

  setAuthenticated: (authenticated) => {
    set({ isAuthenticated: authenticated });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error });
  },

  login: (user, token, refreshToken) => {
    set({
      user,
      token,
      refreshToken: refreshToken || null,
      isAuthenticated: true,
      userRole: user.role,
      error: null,
    });
    localStorage.setItem('ciaf_user', JSON.stringify(user));
    localStorage.setItem('ciaf_jwt_token', token);
    if (refreshToken) {
      localStorage.setItem('ciaf_refresh_token', refreshToken);
    }
  },

  logout: () => {
    set({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      userRole: null,
      error: null,
    });
    localStorage.removeItem('ciaf_user');
    localStorage.removeItem('ciaf_jwt_token');
    localStorage.removeItem('ciaf_refresh_token');
  },

  refreshAccessToken: (newToken) => {
    set({ token: newToken });
    localStorage.setItem('ciaf_jwt_token', newToken);
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

  clearError: () => {
    set({ error: null });
  },

  hydrate: () => {
    const storedUser = localStorage.getItem('ciaf_user');
    const storedToken = localStorage.getItem('ciaf_jwt_token');
    const storedRefreshToken = localStorage.getItem('ciaf_refresh_token');

    if (storedUser && storedToken) {
      const user = JSON.parse(storedUser) as User;
      set({
        user,
        token: storedToken,
        refreshToken: storedRefreshToken,
        isAuthenticated: true,
        userRole: user.role,
      });
    }
  },
}));
