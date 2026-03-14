import React, { useMemo, useState } from 'react';
import { useHealthCheck, useOrganizationStats } from '@/api/hooks';
import { RiskBadge, LoadingSpinner } from '@/components/common/Badges';
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
    return <LoadingSpinner message="Loading dashboard..." />;
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
    <div className="p-8 space-y-8">
      {/* Organization Selector */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Organization</h2>
        <div className="flex gap-3 flex-wrap">
          {ORGANIZATIONS.map((org) => (
            <button
              key={org.id}
              onClick={() => setSelectedOrg(org.id)}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                selectedOrg === org.id
                  ? 'bg-blue-600 text-white shadow'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {org.label}
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-600 mt-3">
          Selected: <span className="font-mono text-blue-600">{selectedOrg}</span>
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Outputs</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {totalTags.toLocaleString()}
              </p>
            </div>
            <Activity className="text-blue-600" size={40} strokeWidth={1} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Verification Rate</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{verificationRate}%</p>
            </div>
            <CheckCircle2 className="text-green-600" size={40} strokeWidth={1} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">High Risk Outputs</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {highRiskTags}
              </p>
            </div>
            <AlertCircle className="text-red-600" size={40} strokeWidth={1} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Service Status</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {health?.status === 'healthy' ? 'Healthy' : 'Issues'}
              </p>
            </div>
            <Zap className="text-green-600" size={40} strokeWidth={1} />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-2 gap-6">
        {/* Risk Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
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
            <div className="h-[300px] flex items-center justify-center bg-gray-50 rounded">
              <p className="text-gray-500">No data available yet</p>
            </div>
          )}
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
              <span className="text-gray-600 font-medium">Output Tags</span>
              <span className="font-semibold text-lg">{outputTagsCount.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded">
              <span className="text-gray-600 font-medium">Verified Tags</span>
              <span className="font-semibold text-lg text-green-600">{verifiedTags.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-purple-50 rounded">
              <span className="text-gray-600 font-medium">Task Batches</span>
              <span className="font-semibold text-lg">{taskBatchesCount.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-orange-50 rounded">
              <span className="text-gray-600 font-medium">Org Batch Windows</span>
              <span className="font-semibold text-lg">{orgBatchWindowsCount.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded">
              <span className="text-gray-600 font-medium">Critical Outputs</span>
              <span className="font-semibold text-lg text-red-600">{criticalTags}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Organization Stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Organization Statistics</h3>
        <div className="grid grid-cols-3 gap-6">
          <div className="border-l-4 border-blue-500 pl-4">
            <p className="text-gray-600 text-sm">Organization ID</p>
            <p className="text-lg font-mono text-blue-600 mt-1">{selectedOrg}</p>
          </div>
          <div className="border-l-4 border-green-500 pl-4">
            <p className="text-gray-600 text-sm">Total Tags</p>
            <p className="text-lg font-bold text-green-600 mt-1">{totalTags}</p>
          </div>
          <div className="border-l-4 border-purple-500 pl-4">
            <p className="text-gray-600 text-sm">Batch Windows</p>
            <p className="text-lg font-bold text-purple-600 mt-1">{stats?.total_batch_windows || 0}</p>
          </div>
        </div>
      </div>

      {/* Quick Action Buttons */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-4 gap-4">
          <Link
            to="/verify"
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-center font-medium transition-colors"
          >
            Verify Output
          </Link>
          <Link
            to="/audit"
            className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-center font-medium transition-colors"
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
