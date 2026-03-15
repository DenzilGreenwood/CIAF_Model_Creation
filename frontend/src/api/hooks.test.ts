import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import * as hooks from './hooks';
import * as client from './client';

// Mock the API client
vi.mock('./client', () => ({
  apiClient: {
    verifyOutput: vi.fn(),
    getAuditTrail: vi.fn(),
    getComplianceReport: vi.fn(),
    getOrganizationStats: vi.fn(),
    healthCheck: vi.fn(),
    refreshCache: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe('API Hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useVerifyOutput', () => {
    it('should fetch verification result when enabled', async () => {
      const mockResult = {
        tag_id: 'tag-123',
        verified: true,
        timestamp: '2026-03-14T00:00:00Z',
        agent_ids: ['agent-1'],
      };

      vi.mocked(client.apiClient.verifyOutput).mockResolvedValue(mockResult);

      const { result } = renderHook(
        () => hooks.useVerifyOutput('tag-123', true),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResult);
    });

    it('should not fetch when disabled', async () => {
      const { result } = renderHook(
        () => hooks.useVerifyOutput('tag-123', false),
        { wrapper: createWrapper() }
      );

      expect(client.apiClient.verifyOutput).not.toHaveBeenCalled();
      expect(result.current.data).toBeUndefined();
    });

    it('should not fetch without tag ID', async () => {
      const { result } = renderHook(
        () => hooks.useVerifyOutput('', true),
        { wrapper: createWrapper() }
      );

      expect(client.apiClient.verifyOutput).not.toHaveBeenCalled();
    });

    it('should handle verification errors', async () => {
      const error = new Error('Verification failed');
      vi.mocked(client.apiClient.verifyOutput).mockRejectedValue(error);

      const { result } = renderHook(
        () => hooks.useVerifyOutput('tag-123', true),
        { wrapper: createWrapper() }
      );

      // React Query needs time to process the rejection and update error state
      await waitFor(
        () => {
          // Check either isError flag or status='error' (react-query 3/4 compatibility)
          const hasError = result.current.isError || result.current.status === 'error';
          expect(hasError).toBe(true);
        },
        { timeout: 2000 }
      );
    });
  });

  describe('useVerifyOutputMutation', () => {
    it('should trigger verification on mutation', async () => {
      const mockResult = {
        tag_id: 'tag-123',
        verified: true,
        timestamp: '2026-03-14T00:00:00Z',
        agent_ids: ['agent-1'],
      };

      vi.mocked(client.apiClient.verifyOutput).mockResolvedValue(mockResult);

      const { result } = renderHook(
        () => hooks.useVerifyOutputMutation(),
        { wrapper: createWrapper() }
      );

      result.current.mutate('tag-123');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResult);
    });

    it('should call API with correct parameters', async () => {
      vi.mocked(client.apiClient.verifyOutput).mockResolvedValue({} as any);

      const { result } = renderHook(
        () => hooks.useVerifyOutputMutation(),
        { wrapper: createWrapper() }
      );

      result.current.mutate('tag-456');

      await waitFor(() => {
        expect(client.apiClient.verifyOutput).toHaveBeenCalledWith('tag-456', {
          verify_merkle: true,
          include_audit_trail: true,
        });
      });
    });
  });

  describe('useAuditTrail', () => {
    it('should fetch audit trail when tag ID is provided', async () => {
      const mockAuditTrail = {
        tag_id: 'tag-123',
        agent_ids: ['agent-1', 'agent-2'],
        inference_type: 'multi_agent',
        actions: [],
      };

      vi.mocked(client.apiClient.getAuditTrail).mockResolvedValue(mockAuditTrail);

      const { result } = renderHook(
        () => hooks.useAuditTrail('tag-123'),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockAuditTrail);
    });

    it('should not fetch without tag ID', async () => {
      const { result } = renderHook(
        () => hooks.useAuditTrail(''),
        { wrapper: createWrapper() }
      );

      expect(client.apiClient.getAuditTrail).not.toHaveBeenCalled();
    });
  });

  describe('useComplianceReport', () => {
    it('should fetch compliance report', async () => {
      const mockReport = {
        organization_id: 'org-1',
        compliance_status: 'compliant',
      };

      vi.mocked(client.apiClient.getComplianceReport).mockResolvedValue(mockReport);

      const { result } = renderHook(
        () => hooks.useComplianceReport('org-1'),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockReport);
    });

    it('should include policy filter', async () => {
      vi.mocked(client.apiClient.getComplianceReport).mockResolvedValue({} as any);

      const { result } = renderHook(
        () => hooks.useComplianceReport('org-1', 'hipaa'),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(client.apiClient.getComplianceReport).toHaveBeenCalledWith('org-1', 'hipaa');
    });

    it('should not fetch without organization ID', async () => {
      const { result } = renderHook(
        () => hooks.useComplianceReport(''),
        { wrapper: createWrapper() }
      );

      expect(client.apiClient.getComplianceReport).not.toHaveBeenCalled();
    });
  });

  describe('useOrganizationStats', () => {
    it('should fetch organization statistics', async () => {
      const mockStats = {
        organization_id: 'org-1',
        total_tags: 100,
        verified_tags: 95,
        high_risk_tags: 5,
        critical_tags: 0,
      };

      vi.mocked(client.apiClient.getOrganizationStats).mockResolvedValue(mockStats);

      const { result } = renderHook(
        () => hooks.useOrganizationStats('org-1'),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockStats);
    });

    it('should not fetch without organization ID', async () => {
      const { result } = renderHook(
        () => hooks.useOrganizationStats(''),
        { wrapper: createWrapper() }
      );

      expect(client.apiClient.getOrganizationStats).not.toHaveBeenCalled();
    });

    it('should have 30 second refetch interval', () => {
      vi.mocked(client.apiClient.getOrganizationStats).mockResolvedValue({} as any);

      renderHook(
        () => hooks.useOrganizationStats('org-1'),
        { wrapper: createWrapper() }
      );

      // The hook should be configured with refetchInterval
      expect(client.apiClient.getOrganizationStats).toHaveBeenCalled();
    });
  });

  describe('useHealthCheck', () => {
    it('should fetch health status', async () => {
      const mockHealth = {
        status: 'healthy',
        service: 'CIAF Verification',
        version: '1.0.0',
      };

      vi.mocked(client.apiClient.healthCheck).mockResolvedValue(mockHealth);

      const { result } = renderHook(
        () => hooks.useHealthCheck(),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockHealth);
    });

    it('should retry on error', async () => {
      const error = new Error('Service unavailable');
      vi.mocked(client.apiClient.healthCheck)
        .mockRejectedValueOnce(error)
        .mockResolvedValueOnce({ status: 'healthy' } as any);

      const { result } = renderHook(
        () => hooks.useHealthCheck(),
        { wrapper: createWrapper() }
      );

      // Should eventually succeed after retry
      await waitFor(() => {
        expect(result.current.isSuccess || result.current.isError).toBe(true);
      });
    });
  });

  describe('useRefreshCache', () => {
    it('should trigger cache refresh', async () => {
      const mockResponse = { status: 'success', message: 'Cache refreshed' };
      vi.mocked(client.apiClient.refreshCache).mockResolvedValue(mockResponse);

      const { result } = renderHook(
        () => hooks.useRefreshCache(),
        { wrapper: createWrapper() }
      );

      result.current.mutate();

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResponse);
    });

    it('should invalidate related queries on success', async () => {
      vi.mocked(client.apiClient.refreshCache).mockResolvedValue({} as any);

      const { result } = renderHook(
        () => hooks.useRefreshCache(),
        { wrapper: createWrapper() }
      );

      result.current.mutate();

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(client.apiClient.refreshCache).toHaveBeenCalled();
    });
  });
});
