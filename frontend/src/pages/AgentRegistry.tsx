import React, { useState, useMemo } from 'react';
import { Search, Plus, Zap, AlertCircle, CheckCircle2, Clock, Settings, Trash2 } from 'lucide-react';
import { RiskBadge } from '@/components/common/Badges';

interface Agent {
  agent_id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  role: string;
  organization_id: string;
  last_activity: string;
  success_rate: number;
  total_executions: number;
  policies: string[];
  created_at: string;
}

const MOCK_AGENTS: Agent[] = [
  {
    agent_id: 'agent-classifier-001',
    name: 'Banking Classifier',
    status: 'active',
    role: 'classifier',
    organization_id: 'banking_org_001',
    last_activity: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    success_rate: 99.8,
    total_executions: 1250,
    policies: ['policy-gdpr', 'policy-aml', 'policy-fair-lending'],
    created_at: '2026-01-15T10:30:00Z',
  },
  {
    agent_id: 'agent-validator-001',
    name: 'Healthcare Validator',
    status: 'active',
    role: 'validator',
    organization_id: 'healthcare_org_001',
    last_activity: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
    success_rate: 98.5,
    total_executions: 890,
    policies: ['policy-hipaa', 'policy-bias-detection'],
    created_at: '2026-01-20T14:20:00Z',
  },
  {
    agent_id: 'agent-orchestrator-001',
    name: 'Compliance Orchestrator',
    status: 'active',
    role: 'orchestrator',
    organization_id: 'banking_org_001',
    last_activity: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    success_rate: 99.2,
    total_executions: 2100,
    policies: ['policy-sox', 'policy-gdpr', 'policy-aml'],
    created_at: '2026-02-01T08:45:00Z',
  },
  {
    agent_id: 'agent-auditor-001',
    name: 'Audit Trail Agent',
    status: 'inactive',
    role: 'auditor',
    organization_id: 'multi_org_001',
    last_activity: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    success_rate: 100,
    total_executions: 450,
    policies: ['policy-audit-logging'],
    created_at: '2026-02-10T16:00:00Z',
  },
  {
    agent_id: 'agent-transformer-001',
    name: 'Data Transformer',
    status: 'error',
    role: 'transformer',
    organization_id: 'healthcare_org_001',
    last_activity: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    success_rate: 85.3,
    total_executions: 620,
    policies: ['policy-pii-masking'],
    created_at: '2026-02-15T11:25:00Z',
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'text-green-400 bg-green-400/10';
    case 'inactive':
      return 'text-yellow-400 bg-yellow-400/10';
    case 'error':
      return 'text-red-400 bg-red-400/10';
    default:
      return 'text-slate-400 bg-slate-400/10';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active':
      return <CheckCircle2 size={16} />;
    case 'inactive':
      return <Clock size={16} />;
    case 'error':
      return <AlertCircle size={16} />;
    default:
      return null;
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60 * 1000) return 'Just now';
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}m ago`;
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}h ago`;
  if (diff < 7 * 24 * 60 * 60 * 1000) return `${Math.floor(diff / (24 * 60 * 60 * 1000))}d ago`;

  return date.toLocaleDateString();
};

export const AgentRegistry: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const filteredAgents = useMemo(() => {
    return MOCK_AGENTS.filter((agent) => {
      // Filter by search
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          agent.agent_id.toLowerCase().includes(query) ||
          agent.name.toLowerCase().includes(query) ||
          agent.role.toLowerCase().includes(query)
        );
      }

      // Filter by role
      if (selectedRole !== 'all' && agent.role !== selectedRole) {
        return false;
      }

      // Filter by status
      if (selectedStatus !== 'all' && agent.status !== selectedStatus) {
        return false;
      }

      return true;
    });
  }, [searchQuery, selectedRole, selectedStatus]);

  const roleOptions = ['all', ...new Set(MOCK_AGENTS.map((a) => a.role))];
  const statusOptions = ['all', 'active', 'inactive', 'error'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Agent Registry</h1>
        <p className="text-slate-400">Manage and monitor AI agents in your organization</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="text-sm text-slate-400 mb-1">Total Agents</div>
          <div className="text-2xl font-bold text-white">{MOCK_AGENTS.length}</div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="text-sm text-slate-400 mb-1">Active</div>
          <div className="text-2xl font-bold text-green-400">
            {MOCK_AGENTS.filter((a) => a.status === 'active').length}
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="text-sm text-slate-400 mb-1">Avg Success Rate</div>
          <div className="text-2xl font-bold text-cyan-400">
            {(MOCK_AGENTS.reduce((sum, a) => sum + a.success_rate, 0) / MOCK_AGENTS.length).toFixed(1)}%
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="text-sm text-slate-400 mb-1">Total Executions</div>
          <div className="text-2xl font-bold text-purple-400">
            {MOCK_AGENTS.reduce((sum, a) => sum + a.total_executions, 0).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" size={20} />
          <input
            type="text"
            placeholder="Search agents by ID, name, or role..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>

        {/* Filters */}
        <select
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value)}
          className="px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          {roleOptions.map((role) => (
            <option key={role} value={role}>
              {role === 'all' ? 'All Roles' : role.charAt(0).toUpperCase() + role.slice(1)}
            </option>
          ))}
        </select>

        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
            </option>
          ))}
        </select>

        {/* Register Button */}
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition">
          <Plus size={20} />
          Register Agent
        </button>
      </div>

      {/* Results */}
      <div className="text-sm text-slate-400 mb-4">
        Showing <span className="text-cyan-400 font-bold">{filteredAgents.length}</span> of{' '}
        <span className="font-bold">{MOCK_AGENTS.length}</span> agents
      </div>

      {/* Agent Cards */}
      <div className="space-y-3">
        {filteredAgents.length > 0 ? (
          filteredAgents.map((agent) => (
            <div
              key={agent.agent_id}
              className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden hover:bg-slate-800/70 transition"
            >
              {/* Agent Header */}
              <div
                onClick={() => setExpandedAgent(expandedAgent === agent.agent_id ? null : agent.agent_id)}
                className="p-4 cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-4 flex-1">
                  {/* Status Icon & Name */}
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(agent.status)}`}>
                      {getStatusIcon(agent.status)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                      <p className="text-sm text-slate-400">{agent.agent_id}</p>
                    </div>
                  </div>

                  {/* Role Badge */}
                  <div className="hidden md:block px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-sm text-purple-400">
                    {agent.role}
                  </div>

                  {/* Success Rate */}
                  <div className="text-right">
                    <div className="text-sm font-bold text-green-400">{agent.success_rate.toFixed(1)}%</div>
                    <div className="text-xs text-slate-500">success rate</div>
                  </div>
                </div>

                {/* Expand Icon */}
                <div className="text-slate-500">
                  {expandedAgent === agent.agent_id ? '−' : '+'}
                </div>
              </div>

              {/* Expanded Details */}
              {expandedAgent === agent.agent_id && (
                <div className="border-t border-slate-700 bg-slate-900/50 p-4 space-y-4">
                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Organization</p>
                      <p className="text-sm text-white font-mono">{agent.organization_id}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Total Executions</p>
                      <p className="text-sm text-cyan-400 font-bold">{agent.total_executions.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Last Activity</p>
                      <p className="text-sm text-white">{formatDate(agent.last_activity)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Created</p>
                      <p className="text-sm text-white">{new Date(agent.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  {/* Policies */}
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Applied Policies</p>
                    <div className="flex flex-wrap gap-2">
                      {agent.policies.map((policy) => (
                        <span
                          key={policy}
                          className="px-2 py-1 bg-blue-500/10 border border-blue-500/20 rounded text-xs text-blue-400"
                        >
                          {policy}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <button className="flex items-center gap-2 px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm transition">
                      <Settings size={16} />
                      Configure
                    </button>
                    <button className="flex items-center gap-2 px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded text-sm transition">
                      <Trash2 size={16} />
                      Remove
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <Zap className="mx-auto text-slate-600 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-slate-400 mb-2">No agents found</h3>
            <p className="text-slate-500">Try adjusting your filters or register a new agent</p>
          </div>
        )}
      </div>
    </div>
  );
};
