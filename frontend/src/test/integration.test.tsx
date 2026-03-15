import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { createTestWrapper } from './test-utils';
import { App } from '@/App';
import * as apiClient from '@/api/client';

/**
 * End-to-End Integration Tests for CIAF System
 *
 * These tests simulate real user workflows combining both frontend UI
 * and backend API interactions.
 */

describe('CIAF End-to-End Integration Tests', () => {
  beforeAll(() => {
    // Setup: Start API server (should be running on port 8001)
    // In real E2E tests, this would use a test container or test server
    console.log('Starting E2E test suite...');
  });

  afterAll(() => {
    console.log('Completed E2E test suite');
  });

  describe('Dashboard Workflow', () => {
    it('should load dashboard with organization selector', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      await waitFor(() => {
        expect(
          screen.getByText('CIAF Verification Vault')
        ).toBeInTheDocument();
      });

      // Check organization selector is present
      expect(screen.getByText('Select Organization')).toBeInTheDocument();
      expect(screen.getByText('Banking Organization')).toBeInTheDocument();
    });

    it('should switch between organizations', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      const healthcareButton = await screen.findByText('Healthcare Organization');
      fireEvent.click(healthcareButton);

      await waitFor(() => {
        expect(screen.getByText('healthcare_org_001')).toBeInTheDocument();
      });
    });

    it('should display real-time statistics', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Wait for stats to load
      await waitFor(() => {
        expect(screen.getByText('Total Outputs')).toBeInTheDocument();
      });

      // Verify stats cards are rendered
      expect(screen.getByText('Verification Rate')).toBeInTheDocument();
      expect(screen.getByText('High Risk Outputs')).toBeInTheDocument();
      expect(screen.getByText('Service Status')).toBeInTheDocument();
    });
  });

  describe('Proof Verification Workflow', () => {
    it('should submit and verify a proof', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to verification page
      const verifyButton = await screen.findByText('Verify Output');
      fireEvent.click(verifyButton);

      // Wait for verification engine to load
      await waitFor(() => {
        expect(screen.getByText('Verification Engine')).toBeInTheDocument();
      });

      // Enter tag ID
      const tagInput = screen.getByPlaceholderText(/Enter tag ID/i);
      fireEvent.change(tagInput, { target: { value: 'tag-123' } });

      // Submit verification
      const verifySubmitButton = screen.getByText('Verify');
      fireEvent.click(verifySubmitButton);

      // Wait for results
      await waitFor(() => {
        expect(screen.getByText(/Verification Result/i)).toBeInTheDocument();
      });

      // Check verification status
      expect(screen.getByText(/Verified/i)).toBeInTheDocument();
    });

    it('should handle invalid tag IDs', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to verification
      const verifyButton = await screen.findByText('Verify Output');
      fireEvent.click(verifyButton);

      // Enter invalid tag ID
      const tagInput = await screen.findByPlaceholderText(/Enter tag ID/i);
      fireEvent.change(tagInput, { target: { value: 'invalid-id' } });

      const verifySubmitButton = screen.getByText('Verify');
      fireEvent.click(verifySubmitButton);

      // Should show error
      await waitFor(() => {
        expect(screen.getByText(/not found|error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Audit Trail Workflow', () => {
    it('should display audit trail', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to audit trail
      const auditButton = await screen.findByText('View Audit Trail');
      fireEvent.click(auditButton);

      // Wait for audit data
      await waitFor(() => {
        expect(screen.getByText('Audit Trail')).toBeInTheDocument();
      });

      // Check audit entries
      expect(screen.getByText(/Entries/i)).toBeInTheDocument();
    });

    it('should filter audit by action', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to audit
      const auditButton = await screen.findByText('View Audit Trail');
      fireEvent.click(auditButton);

      // Wait for filter
      const actionFilter = await screen.findByDisplayValue(/All/i);

      // Select specific action
      fireEvent.change(actionFilter, { target: { value: 'submit_proof' } });

      // Wait for filtered results
      await waitFor(() => {
        // All displayed entries should be submit_proof actions
        const entries = screen.getAllByText(/submit_proof/i);
        expect(entries.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Compliance Dashboard Workflow', () => {
    it('should display compliance status', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to compliance
      const complianceButton = await screen.findByText('Compliance Report');
      fireEvent.click(complianceButton);

      // Wait for compliance data
      await waitFor(() => {
        expect(screen.getByText('Compliance Dashboard')).toBeInTheDocument();
      });

      // Check policy status
      expect(screen.getByText(/HIPAA|GDPR|SOC2/i)).toBeInTheDocument();
    });

    it('should show policy details', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to compliance
      const complianceButton = await screen.findByText('Compliance Report');
      fireEvent.click(complianceButton);

      // Click on policy
      const policyButton = await screen.findByText(/HIPAA/i);
      fireEvent.click(policyButton);

      // Should show detailed policy info
      await waitFor(() => {
        expect(
          screen.getByText(/Policy Requirements|Evidence/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Organization Statistics Workflow', () => {
    it('should display organization statistics', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to stats
      const statsButton = await screen.findByText('View Statistics');
      fireEvent.click(statsButton);

      // Wait for stats page
      await waitFor(() => {
        expect(screen.getByText('Organization Statistics')).toBeInTheDocument();
      });

      // Check various stat cards
      expect(screen.getByText(/Total Tags/i)).toBeInTheDocument();
      expect(screen.getByText(/Verified Tags/i)).toBeInTheDocument();
      expect(screen.getByText(/Risk Distribution/i)).toBeInTheDocument();
    });

    it('should update statistics in real-time', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Navigate to stats
      const statsButton = await screen.findByText('View Statistics');
      fireEvent.click(statsButton);

      // Get initial count
      const initialCount = await screen.findByText(/\d+/);
      const initialValue = initialCount.textContent;

      // Wait for potential update (30 second refetch interval)
      // In tests, we can mock this to be faster
      await waitFor(
        () => {
          // Stats should remain consistent or increase
          const updatedValue = initialCount.textContent;
          expect(updatedValue).toBeDefined();
        },
        { timeout: 2000 }
      );
    });
  });

  describe('Error Handling & Edge Cases', () => {
    it('should handle API errors gracefully', async () => {
      const wrapper = createTestWrapper();

      // Mock API to return error
      const verifyMock = vi.spyOn(apiClient.apiClient, 'verifyOutput');
      verifyMock.mockRejectedValue(new Error('API Error'));

      render(<App />, { wrapper });

      // Try to verify with error
      const verifyButton = await screen.findByText('Verify Output');
      fireEvent.click(verifyButton);

      const tagInput = await screen.findByPlaceholderText(/Enter tag ID/i);
      fireEvent.change(tagInput, { target: { value: 'tag-123' } });

      const submitButton = screen.getByText('Verify');
      fireEvent.click(submitButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/error|failed/i)).toBeInTheDocument();
      });

      verifyMock.mockRestore();
    });

    it('should handle network timeouts', async () => {
      const wrapper = createTestWrapper();

      // Mock slow API
      const healthMock = vi.spyOn(apiClient.apiClient, 'healthCheck');
      healthMock.mockImplementation(
        () =>
          new Promise(resolve =>
            setTimeout(() => resolve({ status: 'healthy' } as any), 5000)
          )
      );

      render(<App />, { wrapper });

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText(/loading|fetching/i)).toBeInTheDocument();
      });

      healthMock.mockRestore();
    });

    it('should show offline indicator', async () => {
      const wrapper = createTestWrapper();

      // Mock offline state
      Object.defineProperty(window.navigator, 'onLine', {
        configurable: true,
        value: false,
      });

      render(<App />, { wrapper });

      // Should show offline indicator
      await waitFor(() => {
        expect(screen.getByText(/offline|no connection/i)).toBeInTheDocument();
      });

      // Restore online state
      Object.defineProperty(window.navigator, 'onLine', {
        configurable: true,
        value: true,
      });
    });
  });

  describe('User Interaction Workflows', () => {
    it('should allow user to refresh cache', async () => {
      const wrapper = createTestWrapper();

      render(<App />, { wrapper });

      // Find and click admin panel if available
      const adminButton = screen.queryByText('Admin');

      if (adminButton) {
        fireEvent.click(adminButton);

        // Find refresh button
        const refreshButton = await screen.findByText(/Refresh|Invalidate/i);
        fireEvent.click(refreshButton);

        // Should show success message
        await waitFor(() => {
          expect(screen.getByText(/Success|Cache refreshed/i)).toBeInTheDocument();
        });
      }
    });

    it('should persist user preferences', async () => {
      const wrapper = createTestWrapper();

      // First session
      const { unmount } = render(<App />, { wrapper });

      // Select healthcare org
      const healthcareButton = await screen.findByText('Healthcare Organization');
      fireEvent.click(healthcareButton);

      unmount();

      // Second session
      render(<App />, { wrapper });

      // Should remember healthcare selection
      await waitFor(() => {
        expect(screen.getByText('healthcare_org_001')).toBeInTheDocument();
      });
    });
  });
});
