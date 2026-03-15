import React, { useMemo, useState } from 'react';
import { useHealthCheck, useOrganizationStats } from '@/api/hooks';
import { RiskBadge } from '@/components/common/Badges';
import { Spinner } from '@/components/common/Spinner';
import { BarChart, Bar, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, CheckCircle2, AlertCircle, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

// Available organizations (from MVP demo)
const ORGANIZATIONS = [
  { id: 'banking_org_001', label: 'Banking Organization' },
  { id: 'healthcare_org_001', label: 'Healthcare Organization' },
  { id: 'multi_org_001', label: 'Multi-Org' },
];

export const Dashboard: React.FC = () => {
  const [selectedOrg, setSelectedOrg] = useState('banking_org_001');
  const { data: health, isLoading: healthLoading } = useHealthCheck();
  const { data: stats, isLoading: statsLoading } = useOrganizationStats(selectedOrg);

  const riskDistribution = useMemo(() => {
    if (!stats) return [];

    // Safely compute values with fallbacks
    const totalTags = stats.total_tags || 0;
    const highRiskTags = stats.high_risk_tags || 0;
    const criticalTags = stats.critical_tags || 0;
    const lowRiskTags = totalTags - highRiskTags - criticalTags;

    return [
      { name: 'Low Risk', value: Math.max(0, lowRiskTags), color: '#10b981' },
      { name: 'High Risk', value: highRiskTags, color: '#ef4444' },
      { name: 'Critical', value: criticalTags, color: '#7c3aed' },
    ].filter(item => item.value > 0);
  }, [stats]);

  if (healthLoading || statsLoading) {
    return <Spinner message="Loading dashboard..." />;
  }

  // Safe calculations with fallbacks
  const totalTags = stats?.total_tags || 0;
  const verifiedTags = stats?.verified_tags || 0;
  const highRiskTags = stats?.high_risk_tags || 0;
  const criticalTags = stats?.critical_tags || 0;
  const verificationRate = totalTags > 0 ? ((verifiedTags / totalTags) * 100).toFixed(1) : '0';

  // Safe health check stats access
  const proofStoreStats = health?.proof_store_stats || {};
  const outputTagsCount = proofStoreStats.output_tags || 0;
  const taskBatchesCount = proofStoreStats.task_batches || 0;
  const orgBatchWindowsCount = proofStoreStats.org_batch_windows || 0;

  return (
    <div className="p-8 space-y-8 bg-slate-950">
      {/* Organization Selector */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-slate-50 mb-4">Select Organization</h2>
        <div className="flex gap-3 flex-wrap">
          {ORGANIZATIONS.map((org) => (
            <button
              key={org.id}
              onClick={() => setSelectedOrg(org.id)}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                selectedOrg === org.id
                  ? 'bg-blue-600 text-white shadow'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-cyan-400'
              }`}
            >
              {org.label}
            </button>
          ))}
        </div>
        <p className="text-sm text-slate-400 mt-3">
          Selected: <span className="font-mono text-cyan-400">{selectedOrg}</span>
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6 hover:border-blue-500 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm font-medium">Total Outputs</p>
              <p className="text-3xl font-bold text-slate-50 mt-2">
                {totalTags.toLocaleString()}
              </p>
            </div>
            <Activity className="text-blue-500" size={40} strokeWidth={1} />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6 hover:border-cyan-400 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm font-medium">Verification Rate</p>
              <p className="text-3xl font-bold text-cyan-400 mt-2">{verificationRate}%</p>
            </div>
            <CheckCircle2 className="text-cyan-400" size={40} strokeWidth={1} />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6 hover:border-orange-500 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm font-medium">High Risk Outputs</p>
              <p className="text-3xl font-bold text-orange-500 mt-2">
                {highRiskTags}
              </p>
            </div>
            <AlertCircle className="text-orange-500" size={40} strokeWidth={1} />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6 hover:border-green-500 transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm font-medium">Service Status</p>
              <p className="text-3xl font-bold text-green-500 mt-2">
                {health?.status === 'healthy' ? 'Healthy' : 'Issues'}
              </p>
            </div>
            <Zap className="text-green-500" size={40} strokeWidth={1} />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-2 gap-6">
        {/* Risk Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">Risk Distribution</h3>
          {riskDistribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center bg-slate-800 rounded">
              <p className="text-slate-500">No data available yet</p>
            </div>
          )}
        </div>

        {/* System Health */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-slate-50 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-800 border border-slate-700 rounded">
              <span className="text-slate-300 font-medium">Output Tags</span>
              <span className="font-semibold text-lg text-blue-400">{outputTagsCount.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800 border border-slate-700 rounded">
              <span className="text-slate-300 font-medium">Verified Tags</span>
              <span className="font-semibold text-lg text-cyan-400">{verifiedTags.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800 border border-slate-700 rounded">
              <span className="text-slate-300 font-medium">Task Batches</span>
              <span className="font-semibold text-lg text-blue-400">{taskBatchesCount.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800 border border-slate-700 rounded">
              <span className="text-slate-300 font-medium">Org Batch Windows</span>
              <span className="font-semibold text-lg text-orange-400">{orgBatchWindowsCount.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800 border border-slate-700 rounded">
              <span className="text-slate-300 font-medium">Critical Outputs</span>
              <span className="font-semibold text-lg text-red-500">{criticalTags}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Organization Stats */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-slate-50 mb-4">Organization Statistics</h3>
        <div className="grid grid-cols-3 gap-6">
          <div className="border-l-4 border-blue-500 pl-4">
            <p className="text-slate-400 text-sm">Organization ID</p>
            <p className="text-lg font-mono text-cyan-400 mt-1">{selectedOrg}</p>
          </div>
          <div className="border-l-4 border-cyan-400 pl-4">
            <p className="text-slate-400 text-sm">Total Tags</p>
            <p className="text-lg font-bold text-cyan-400 mt-1">{totalTags}</p>
          </div>
          <div className="border-l-4 border-blue-600 pl-4">
            <p className="text-slate-400 text-sm">Batch Windows</p>
            <p className="text-lg font-bold text-blue-400 mt-1">{stats?.total_batch_windows || 0}</p>
          </div>
        </div>
      </div>

      {/* Quick Action Buttons */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-slate-50 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-4 gap-4">
          <Link
            to="/verify"
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-center font-medium transition-colors"
          >
            Verify Output
          </Link>
          <Link
            to="/audit"
            className="px-4 py-3 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 text-center font-medium transition-colors"
          >
            View Audit Trail
          </Link>
          <Link
            to="/compliance"
            className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 text-center font-medium transition-colors"
          >
            Compliance Report
          </Link>
          <Link
            to="/stats"
            className="px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-center font-medium transition-colors"
          >
            View Statistics
          </Link>
        </div>
      </div>
    </div>
  );
};
