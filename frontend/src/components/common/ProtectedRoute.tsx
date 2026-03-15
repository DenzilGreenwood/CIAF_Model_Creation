import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth.store';
import { UserRole } from '@/types';
import { Spinner } from '@/components/common/Spinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole | UserRole[];
}

/**
 * ProtectedRoute component
 * Ensures only authenticated users can access protected pages
 * Optionally enforces role-based access control
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const location = useLocation();
  const { isAuthenticated, user, hasPermission } = useAuthStore();

  // User is not authenticated - redirect to login
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role-based access if required
  if (requiredRole && !hasPermission(requiredRole)) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-2">Access Denied</h1>
          <p className="text-slate-400 mb-6">
            You don't have permission to access this page.
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

/**
 * Public Route Component
 * Redirects authenticated users away from public pages (login, home)
 * Allows unauthenticated users to access these pages
 */
interface PublicRouteProps<T = any> {
  children: React.ReactNode;
  redirectTo?: string;
}

export const PublicRoute: React.FC<PublicRouteProps> = ({
  children,
  redirectTo = '/dashboard',
}) => {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();

  // Already logged in - redirect to dashboard or specified location
  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
};

/**
 * Admin Only Route
 * Restricts access to admin users only
 */
export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-2">Admin Access Required</h1>
          <p className="text-slate-400">Only administrators can access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
