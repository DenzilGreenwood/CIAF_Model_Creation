import React, { useState } from 'react';
import { Settings, Database, Shield, Users, BarChart3, RefreshCw, AlertCircle, CheckCircle2, Copy, Eye, EyeOff } from 'lucide-react';

interface SystemConfig {
  api_key_length: number;
  default_ttl: number;
  cache_enabled: boolean;
  audit_logging: boolean;
  encryption_algorithm: string;
}

interface ApiKey {
  key_id: string;
  organization_id: string;
  created_at: string;
  last_used: string;
  is_active: boolean;
  permissions: string[];
}

const MOCK_CONFIG: SystemConfig = {
  api_key_length: 32,
  default_ttl: 86400,
  cache_enabled: true,
  audit_logging: true,
  encryption_algorithm: 'Ed25519',
};

const MOCK_API_KEYS: ApiKey[] = [
  {
    key_id: 'key-banking-001',
    organization_id: 'banking_org_001',
    created_at: '2026-01-15T10:30:00Z',
    last_used: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    is_active: true,
    permissions: ['submit_proof', 'verify_proof', 'query_audit_trail'],
  },
  {
    key_id: 'key-healthcare-001',
    organization_id: 'healthcare_org_001',
    created_at: '2026-01-20T14:20:00Z',
    last_used: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    is_active: true,
    permissions: ['submit_proof', 'verify_proof', 'generate_certificate'],
  },
  {
    key_id: 'key-compliance-001',
    organization_id: 'multi_org_001',
    created_at: '2026-02-01T08:45:00Z',
    last_used: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    is_active: false,
    permissions: ['query_audit_trail', 'view_stats'],
  },
];

const SYSTEM_STATS = {
  total_organizations: 3,
  active_api_keys: 2,
  total_proofs: 1247,
  verification_cache_size: '245 MB',
  audit_log_size: '1.2 GB',
  uptime: '45 days 12 hours',
};

export const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'keys' | 'config' | 'security'>('overview');
  const [showKey, setShowKey] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const handleRefreshCache = async () => {
    setRefreshing(true);
    // Simulate refresh
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setRefreshing(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Admin Panel</h1>
        <p className="text-slate-400">Manage system configuration, API keys, and security settings</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-slate-700">
        {['overview', 'keys', 'config', 'security'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 font-medium transition ${
              activeTab === tab
                ? 'text-cyan-400 border-b-2 border-cyan-400'
                : 'text-slate-400 hover:text-slate-300'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* System Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">Total Organizations</div>
              <div className="text-3xl font-bold text-cyan-400">{SYSTEM_STATS.total_organizations}</div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">Active API Keys</div>
              <div className="text-3xl font-bold text-green-400">{SYSTEM_STATS.active_api_keys}</div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">Total Proofs Stored</div>
              <div className="text-3xl font-bold text-purple-400">{SYSTEM_STATS.total_proofs.toLocaleString()}</div>
            </div>

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">Cache Size</div>
              <div className="text-2xl font-bold text-white">{SYSTEM_STATS.verification_cache_size}</div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">Audit Log Size</div>
              <div className="text-2xl font-bold text-white">{SYSTEM_STATS.audit_log_size}</div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">System Uptime</div>
              <div className="text-2xl font-bold text-white">{SYSTEM_STATS.uptime}</div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-4">
            <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={handleRefreshCache}
                disabled={refreshing}
                className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 text-white rounded-lg font-medium transition"
              >
                <RefreshCw size={20} className={refreshing ? 'animate-spin' : ''} />
                {refreshing ? 'Refreshing...' : 'Refresh Cache'}
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition">
                <Database size={20} />
                Export Backup
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium transition">
                <AlertCircle size={20} />
                Run Diagnostics
              </button>
            </div>
          </div>
        </div>
      )}

      {/* API Keys Tab */}
      {activeTab === 'keys' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-white">API Keys</h3>
            <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition">
              + Generate New Key
            </button>
          </div>

          {MOCK_API_KEYS.map((key) => (
            <div key={key.key_id} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`px-3 py-1 rounded text-xs font-medium ${
                    key.is_active
                      ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                      : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                  }`}>
                    {key.is_active ? 'Active' : 'Inactive'}
                  </div>
                  <span className="text-white font-mono text-sm">{key.key_id}</span>
                </div>
                {key.is_active && <CheckCircle2 className="text-green-400" size={20} />}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Organization</p>
                  <p className="text-sm text-white">{key.organization_id}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Created</p>
                  <p className="text-sm text-white">{new Date(key.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Last Used</p>
                  <p className="text-sm text-white">
                    {new Date(key.last_used).toLocaleDateString()} {new Date(key.last_used).toLocaleTimeString()}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Permissions</p>
                  <p className="text-sm text-cyan-400">{key.permissions.length} permissions</p>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Permissions</p>
                <div className="flex flex-wrap gap-2">
                  {key.permissions.map((perm) => (
                    <span key={perm} className="px-2 py-1 bg-blue-500/10 border border-blue-500/20 rounded text-xs text-blue-400">
                      {perm}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm transition">
                  Edit
                </button>
                <button className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded text-sm transition">
                  Revoke
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Configuration Tab */}
      {activeTab === 'config' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">System Configuration</h3>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-6">
            {Object.entries(MOCK_CONFIG).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between pb-4 border-b border-slate-700 last:border-b-0">
                <div>
                  <p className="text-white font-medium capitalize">{key.replace(/_/g, ' ')}</p>
                  <p className="text-sm text-slate-400">Configuration parameter</p>
                </div>
                <div className="text-right">
                  {typeof value === 'boolean' ? (
                    <div className={`px-3 py-1 rounded text-xs font-medium ${
                      value
                        ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                        : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                    }`}>
                      {value ? 'Enabled' : 'Disabled'}
                    </div>
                  ) : (
                    <span className="text-white font-mono text-sm">{value}</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <button className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition">
            Save Changes
          </button>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="space-y-6">
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 flex gap-3">
            <AlertCircle className="text-yellow-400 flex-shrink-0" size={20} />
            <div>
              <h4 className="text-white font-semibold mb-1">Security Notice</h4>
              <p className="text-sm text-yellow-400">All API keys are encrypted and stored securely. Never share your API keys.</p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Security Settings</h3>

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Two-Factor Authentication</p>
                  <p className="text-sm text-slate-400">Require 2FA for admin access</p>
                </div>
                <button className="px-4 py-2 bg-green-600/20 text-green-400 border border-green-500/20 rounded text-sm font-medium">
                  Enabled
                </button>
              </div>
            </div>

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">SSL/TLS Verification</p>
                  <p className="text-sm text-slate-400">Enforce HTTPS for all communications</p>
                </div>
                <button className="px-4 py-2 bg-green-600/20 text-green-400 border border-green-500/20 rounded text-sm font-medium">
                  Enabled
                </button>
              </div>
            </div>

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Rate Limiting</p>
                  <p className="text-sm text-slate-400">API rate limits per organization</p>
                </div>
                <button className="px-4 py-2 bg-green-600/20 text-green-400 border border-green-500/20 rounded text-sm font-medium">
                  Enabled
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white">Audit Log</h3>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm text-slate-400 space-y-2">
                <p>• Admin login: 2026-03-15 10:30 AM</p>
                <p>• Cache refresh: 2026-03-15 09:15 AM</p>
                <p>• API key rotation: 2026-03-14 03:42 PM</p>
                <p>• System backup: 2026-03-14 02:00 AM</p>
              </div>
              <button className="mt-4 text-cyan-400 hover:text-cyan-300 text-sm font-medium transition">
                View Full Audit Log →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
