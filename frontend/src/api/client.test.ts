import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import axios from 'axios';
import { APIClient } from './client';
import { VerificationResult, HealthCheck, OrganizationStats } from '@/types';

// Mock axios
vi.mock('axios');

describe('APIClient', () => {
  let client: APIClient | null = null;
  let mockAxiosInstance: any;

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup mock axios instance with all required methods
    mockAxiosInstance = {
      get: vi.fn().mockResolvedValue({ data: {} }),
      post: vi.fn().mockResolvedValue({ data: {} }),
      put: vi.fn().mockResolvedValue({ data: {} }),
      delete: vi.fn().mockResolvedValue({ data: {} }),
      interceptors: {
        request: { use: vi.fn().mockReturnThis() },
        response: { use: vi.fn().mockReturnThis() },
      },
    };

    // Ensure axios.create returns our mock instance
    const mockedAxios = axios as any;
    mockedAxios.create = vi.fn().mockReturnValue(mockAxiosInstance);

    // Clear localStorage
    localStorage.clear();

    // Now create the client
    client = new APIClient('http://localhost:8001');
  });

  afterEach(() => {
    client = null;
  });

  describe('Initialization', () => {
    it('should create client with default base URL', () => {
      const newClient = new APIClient();
      expect(axios.create).toHaveBeenCalled();
    });

    it('should create client with custom base URL', () => {
      const newClient = new APIClient('http://custom-url:8000');
      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'http://custom-url:8000',
        })
      );
    });

    it('should setup request interceptor', () => {
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
    });

    it('should setup response interceptor', () => {
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('verifyOutput', () => {
    it('should verify output with tag ID', async () => {
      const mockResult: VerificationResult = {
        tag_id: 'tag-123',
        verified: true,
        timestamp: '2026-03-14T00:00:00Z',
        agent_ids: ['agent-1'],
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResult });

      const result = await client.verifyOutput('tag-123');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/verify/tag-123',
        expect.objectContaining({
          params: {
            verify_merkle: true,
            include_audit_trail: true,
          },
        })
      );
      expect(result).toEqual(mockResult);
    });

    it('should pass custom options to verify request', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: {} });

      await client.verifyOutput('tag-123', { verify_merkle: false });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/verify/tag-123',
        expect.objectContaining({
          params: expect.objectContaining({
            verify_merkle: false,
          }),
        })
      );
    });

    it('should handle verification errors', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));

      await expect(client.verifyOutput('tag-123')).rejects.toThrow('Network error');
    });
  });

  describe('verifyOutputPost', () => {
    it('should verify output via POST', async () => {
      const mockResult: VerificationResult = {
        tag_id: 'tag-123',
        verified: true,
        timestamp: '2026-03-14T00:00:00Z',
        agent_ids: ['agent-1'],
      };

      mockAxiosInstance.post.mockResolvedValue({ data: mockResult });

      const result = await client.verifyOutputPost({
        tag_id: 'tag-123',
        verify_merkle: true,
      });

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/verify',
        expect.objectContaining({
          tag_id: 'tag-123',
          verify_merkle: true,
        })
      );
      expect(result).toEqual(mockResult);
    });
  });

  describe('getAuditTrail', () => {
    it('should retrieve audit trail for tag', async () => {
      const mockAuditTrail = {
        tag_id: 'tag-123',
        agent_ids: ['agent-1', 'agent-2'],
        inference_type: 'multi_agent',
        actions: [],
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockAuditTrail });

      const result = await client.getAuditTrail('tag-123');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/audit/tag-123');
      expect(result).toEqual(mockAuditTrail);
    });
  });

  describe('getComplianceReport', () => {
    it('should retrieve compliance report', async () => {
      const mockReport: any = {
        organization_id: 'org-1',
        compliance_status: 'compliant',
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockReport });

      const result = await client.getComplianceReport('org-1');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/compliance/org-1',
        expect.objectContaining({
          params: {},
        })
      );
      expect(result).toEqual(mockReport);
    });

    it('should include policy filter in request', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: {} });

      await client.getComplianceReport('org-1', 'hipaa');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        '/compliance/org-1',
        expect.objectContaining({
          params: { policy: 'hipaa' },
        })
      );
    });
  });

  describe('getOrganizationStats', () => {
    it('should retrieve organization statistics', async () => {
      const mockStats: OrganizationStats = {
        organization_id: 'org-1',
        total_tags: 100,
        verified_tags: 95,
        high_risk_tags: 5,
        critical_tags: 0,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockStats });

      const result = await client.getOrganizationStats('org-1');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/stats/org-1');
      expect(result).toEqual(mockStats);
    });
  });

  describe('healthCheck', () => {
    it('should check service health', async () => {
      const mockHealth: HealthCheck = {
        status: 'healthy',
        service: 'CIAF Verification',
        version: '1.0.0',
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockHealth });

      const result = await client.healthCheck();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockHealth);
    });
  });

  describe('refreshCache', () => {
    it('should trigger cache refresh', async () => {
      const mockResponse = { status: 'success', message: 'Cache refreshed' };

      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await client.refreshCache();

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/admin/refresh-cache', {});
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Request Interceptor', () => {
    it('should add JWT token to headers if present', async () => {
      localStorage.setItem('ciaf_jwt_token', 'test-token-123');

      const interceptorCall = mockAxiosInstance.interceptors.request.use.mock.calls[0][0];
      const config: any = { headers: {} };

      const result = interceptorCall(config);

      expect(result.headers.Authorization).toBe('Bearer test-token-123');
    });

    it('should not add token if not in localStorage', async () => {
      const interceptorCall = mockAxiosInstance.interceptors.request.use.mock.calls[0][0];
      const config: any = { headers: {} };

      const result = interceptorCall(config);

      expect(result.headers.Authorization).toBeUndefined();
    });
  });
});
