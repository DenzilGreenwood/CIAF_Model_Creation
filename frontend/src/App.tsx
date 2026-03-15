import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { ProtectedRoute, PublicRoute, AdminRoute } from '@/components/common/ProtectedRoute';

import {
   Home, 
   Dashboard, 
   VerificationEngine, 
   AuditTrailViewer, 
   ComplianceDashboard, 
   OrganizationStats, 
   AgentRegistry, 
   AdminPanel, 
   NotFound, 
   Login, 
   ForgotPassword, 
   ResetPassword } from '@/pages';

import { useAuthStore } from '@/store/auth.store';
import { NotificationToast } from '@/components/common/NotificationToast';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 10,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  const { user, hydrate, isAuthenticated } = useAuthStore();

  // Hydrate auth state from localStorage
  useEffect(() => {
    hydrate();
  }, [hydrate]);

  // Auto-login for demo if no user (development only)
  useEffect(() => {
    if (!isAuthenticated && !user) {
      // Uncomment for demo mode
      // useAuthStore.setState({
      //   user: {
      //     id: '1',
      //     email: 'demo@ciaf.io',
      //     name: 'Demo User',
      //     role: 'analyst',
      //     organization_id: 'healthcare_org_001',
      //     created_at: new Date().toISOString(),
      //   },
      //   token: 'demo_token_for_development',
      //   isAuthenticated: true,
      //   userRole: 'analyst',
      // });
    }
  }, [isAuthenticated, user]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Public Routes (no layout) */}
          <Route path="/" element={<PublicRoute redirectTo="/dashboard"><Home /></PublicRoute>} />
          <Route path="/home" element={<Navigate to="/" replace />} />

          {/* Authentication Routes */}
          <Route path="/login" element={<PublicRoute redirectTo="/dashboard"><Login /></PublicRoute>} />
          <Route path="/forgot-password" element={<PublicRoute redirectTo="/dashboard"><ForgotPassword /></PublicRoute>} />
          <Route path="/reset-password" element={<PublicRoute redirectTo="/dashboard"><ResetPassword /></PublicRoute>} />

          {/* Protected Routes with MainLayout */}
          <Route
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/verify" element={<VerificationEngine />} />
            <Route path="/audit" element={<AuditTrailViewer />} />
            <Route path="/compliance" element={<ComplianceDashboard />} />
            <Route path="/stats" element={<OrganizationStats />} />
            <Route path="/agents" element={<AgentRegistry />} />

            {/* Admin Only Routes */}
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminPanel />
                </AdminRoute>
              }
            />
          </Route>

          {/* 404 - Not Found (outside MainLayout for full-screen display) */}
          <Route path="*" element={<NotFound />} />
        </Routes>
        <NotificationToast />
      </Router>
    </QueryClientProvider>
  );
};

export default App;
