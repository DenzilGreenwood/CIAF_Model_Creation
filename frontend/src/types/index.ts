// API Response Types - matched to CIAF backend schemas

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type VerificationStatus = 'verified' | 'unverified' | 'pending';
export type InferenceType = 'agent_orchestrated' | 'direct_model';
export type ActionType = 'inference' | 'analysis' | 'decision' | 'escalation';
export type UserRole = 'admin' | 'analyst' | 'auditor' | 'viewer';

export interface AuditAction {
  agent_id: string;
  action_type: ActionType;
  timestamp: string;
  risk_level: RiskLevel;
  status: string;
}

export interface VerificationResult {
  verified: boolean;
  tag_id: string;
  organization_id: string;
  inference_type: InferenceType;
  model_name?: string | null;
  agent_ids: string[];
  policies_applied: string[];
  risk_level: RiskLevel;
  task_batch_verified: boolean;
  org_batch_verified: boolean;
  merkle_proof_valid: boolean;
  agent_audit_trail: AuditAction[];
  issues: string[];
  warnings: string[];
  timestamp?: string;
}

export interface ComplianceReport {
  organization_id: string;
  policy: string;
  total_outputs: number;
  policy_covered: number;
  compliance_rate: number;
  verified_outputs: number;
}

export interface OrganizationStats {
  organization_id: string;
  total_tags: number;
  verified_tags: number;
  high_risk_tags: number;
  critical_tags: number;
  total_batch_windows: number;
}

export interface Agent {
  agent_id: string;
  agent_name: string;
  organization_id: string;
  description: string;
  policies_applied: string[];
  is_active: boolean;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  organization_id: string;
  created_at: string;
  last_login?: string;
}

export interface HealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: string;
  proof_store_stats?: {
    output_tags?: number;
    task_batches?: number;
    org_batch_windows?: number;
    output_tags_count?: number;
    task_batches_count?: number;
    org_batch_windows_count?: number;
    agent_actions_count?: number;
    verification_cache_hits?: number;
    last_sync?: string;
  };
}

export interface SearchFilters {
  organization_id?: string;
  agent_id?: string;
  risk_level?: RiskLevel;
  policy?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  searchQuery?: string;
}
