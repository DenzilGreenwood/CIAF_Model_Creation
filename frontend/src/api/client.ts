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

  async getAuditTrailEntries(organizationId: string, options?: {
    action?: string;
    start_time?: string;
    end_time?: string;
    limit?: number;
  }): Promise<{
    entries: any[];
    total: number;
    organization_id: string;
  }> {
    const response = await this.client.get('/audit-trail', {
      params: options,
    });
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

  // ============================================================
  // Authentication endpoints
  // ============================================================

  async login(email: string, password: string): Promise<{
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: {
      id: string;
      email: string;
      name: string;
      role: string;
      organization_id: string;
    };
  }> {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async logout(): Promise<{ status: string; message: string }> {
    const response = await this.client.post('/auth/logout', {});
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{
    access_token: string;
    token_type: string;
  }> {
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  async requestPasswordReset(email: string): Promise<{
    message: string;
    status: string;
  }> {
    const response = await this.client.post('/auth/password-reset', { email });
    return response.data;
  }

  async confirmPasswordReset(token: string, newPassword: string): Promise<{
    message: string;
    status: string;
  }> {
    const response = await this.client.post('/auth/password-reset-confirm', {
      token,
      new_password: newPassword,
    });
    return response.data;
  }

  async verifyEmail(token: string): Promise<{
    message: string;
    status: string;
  }> {
    const response = await this.client.post('/auth/verify-email', { token });
    return response.data;
  }
}

export const apiClient = new APIClient();
