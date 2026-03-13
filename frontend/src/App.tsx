import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout/MainLayout';
import { Dashboard } from '@/pages/Dashboard';
import { VerificationEngine } from '@/pages/VerificationEngine';
import { ComplianceDashboard } from '@/pages/ComplianceDashboard';
import { OrganizationStats } from '@/pages/OrganizationStats';
import { AuditTrailViewer, AgentRegistry, AdminPanel, NotFound } from '@/pages';
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
  const { user, hydrate } = useAuthStore();

  // Hydrate auth state from localStorage
  useEffect(() => {
    hydrate();
  }, [hydrate]);

  // If no user, redirect to login (or use mock user for demo)
  if (!user) {
    // For demo purposes, auto-login
    useAuthStore.setState({
      user: {
        id: '1',
        email: 'demo@ciaf.io',
        name: 'Demo User',
        role: 'analyst',
        organization_id: 'healthcare_org_001',
        created_at: new Date().toISOString(),
      },
      token: 'demo_token_for_development',
      isAuthenticated: true,
      userRole: 'analyst',
    });
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/verify" element={<VerificationEngine />} />
            <Route path="/audit" element={<AuditTrailViewer />} />
            <Route path="/compliance" element={<ComplianceDashboard />} />
            <Route path="/stats" element={<OrganizationStats />} />
            <Route path="/agents" element={<AgentRegistry />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
        <NotificationToast />
      </Router>
    </QueryClientProvider>
  );
};

export default App;
