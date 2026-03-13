import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import { VerificationResult, HealthCheck, OrganizationStats, ComplianceReport } from '@/types';

export class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add JWT token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('ciaf_jwt_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('ciaf_jwt_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Verification endpoints
  async verifyOutput(tagId: string, options?: {
    verify_merkle?: boolean;
    include_audit_trail?: boolean;
  }): Promise<VerificationResult> {
    const response = await this.client.get<VerificationResult>(`/verify/${tagId}`, {
      params: options,
    });
    return response.data;
  }

  async verifyOutputPost(payload: {
    tag_id: string;
    verify_merkle?: boolean;
    include_audit_trail?: boolean;
  }): Promise<VerificationResult> {
    const response = await this.client.post<VerificationResult>('/verify', payload);
    return response.data;
  }

  // Audit endpoints
  async getAuditTrail(tagId: string): Promise<{
    tag_id: string;
    agent_ids: string[];
    inference_type: string;
    model_name?: string;
    actions: any[];
  }> {
    const response = await this.client.get(`/audit/${tagId}`);
    return response.data;
  }

  // Compliance endpoints
  async getComplianceReport(
    organizationId: string,
    policy?: string
  ): Promise<ComplianceReport> {
    const response = await this.client.get<ComplianceReport>(
      `/compliance/${organizationId}`,
      { params: { policy } }
    );
    return response.data;
  }

  // Statistics endpoints
  async getOrganizationStats(organizationId: string): Promise<OrganizationStats> {
    const response = await this.client.get<OrganizationStats>(
      `/stats/${organizationId}`
    );
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<HealthCheck> {
    const response = await this.client.get<HealthCheck>('/health');
    return response.data;
  }

  // Admin endpoints
  async refreshCache(): Promise<{ status: string; message: string }> {
    const response = await this.client.post('/admin/refresh-cache', {});
    return response.data;
  }
}

export const apiClient = new APIClient();
