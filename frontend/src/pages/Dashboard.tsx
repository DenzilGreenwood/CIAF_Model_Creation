import React, { useMemo } from 'react';
import { useHealthCheck, useOrganizationStats } from '@/api/hooks';
import { RiskBadge, LoadingSpinner } from '@/components/common/Badges';
import { BarChart, Bar, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, CheckCircle2, AlertCircle, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const { data: health, isLoading: healthLoading } = useHealthCheck();
  const { data: stats, isLoading: statsLoading } = useOrganizationStats('healthcare_org_001');

  const riskDistribution = useMemo(() => {
    if (!stats) return [];
    return [
      { name: 'Low Risk', value: stats.total_tags - stats.high_risk_tags - stats.critical_tags, color: '#10b981' },
      { name: 'High Risk', value: stats.high_risk_tags, color: '#ef4444' },
      { name: 'Critical', value: stats.critical_tags, color: '#7c3aed' },
    ];
  }, [stats]);

  if (healthLoading || statsLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  const verificationRate = stats ? ((stats.verified_tags / stats.total_tags) * 100).toFixed(1) : '0';

  return (
    <div className="p-8 space-y-8">
      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Outputs</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.total_tags.toLocaleString() || '0'}
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
                {stats?.high_risk_tags || '0'}
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
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Output Tags</span>
              <span className="font-semibold">{health?.proof_store_stats?.output_tags_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Task Batches</span>
              <span className="font-semibold">{health?.proof_store_stats?.task_batches_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Org Batch Windows</span>
              <span className="font-semibold">{health?.proof_store_stats?.org_batch_windows_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Agent Actions</span>
              <span className="font-semibold">{health?.proof_store_stats?.agent_actions_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Cache Hits</span>
              <span className="font-semibold">{health?.proof_store_stats?.verification_cache_hits.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Action Buttons */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-4 gap-4">
          <Link
            to="/verify"
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-center font-medium"
          >
            Verify Output
          </Link>
          <Link
            to="/audit"
            className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-center font-medium"
          >
            View Audit Trail
          </Link>
          <Link
            to="/compliance"
            className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 text-center font-medium"
          >
            Compliance Report
          </Link>
          <Link
            to="/stats"
            className="px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-center font-medium"
          >
            View Statistics
          </Link>
        </div>
      </div>
    </div>
  );
};
