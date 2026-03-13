import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { VerificationResult, OrganizationStats, ComplianceReport } from '@/types';

// Verification Hooks
export const useVerifyOutput = (tagId: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['verification', tagId],
    queryFn: () => apiClient.verifyOutput(tagId, {
      verify_merkle: true,
      include_audit_trail: true,
    }),
    enabled: enabled && !!tagId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
  });
};

export const useVerifyOutputMutation = () => {
  return useMutation({
    mutationFn: (tagId: string) => apiClient.verifyOutput(tagId, {
      verify_merkle: true,
      include_audit_trail: true,
    }),
  });
};

// Audit Trail Hooks
export const useAuditTrail = (tagId: string) => {
  return useQuery({
    queryKey: ['audit', tagId],
    queryFn: () => apiClient.getAuditTrail(tagId),
    enabled: !!tagId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Compliance Hooks
export const useComplianceReport = (organizationId: string, policy?: string) => {
  return useQuery({
    queryKey: ['compliance', organizationId, policy],
    queryFn: () => apiClient.getComplianceReport(organizationId, policy),
    enabled: !!organizationId,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

// Organization Stats Hooks
export const useOrganizationStats = (organizationId: string) => {
  return useQuery({
    queryKey: ['stats', organizationId],
    queryFn: () => apiClient.getOrganizationStats(organizationId),
    enabled: !!organizationId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // 30 seconds (real-time updates)
  });
};

// Health Check Hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 30 * 1000, // 30 seconds
  });
};

// Admin Hooks
export const useRefreshCache = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.refreshCache(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['verification'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      queryClient.invalidateQueries({ queryKey: ['compliance'] });
    },
  });
};
