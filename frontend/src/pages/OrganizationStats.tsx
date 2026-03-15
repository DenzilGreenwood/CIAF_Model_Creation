import React from 'react';
import { useOrganizationStats } from '@/api/hooks';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Spinner } from '@/components/common/Spinner';

export const OrganizationStats: React.FC = () => {
  const { data: stats, isLoading } = useOrganizationStats('healthcare_org_001');

  if (isLoading) {
    return <Spinner message="Loading statistics..." />;
  }

  if (!stats) {
    return <div className="p-8 text-center text-gray-600">No data available</div>;
  }

  const riskData = [
    {
      name: 'Low',
      value: stats.total_tags - stats.high_risk_tags - stats.critical_tags,
    },
    { name: 'High', value: stats.high_risk_tags },
    { name: 'Critical', value: stats.critical_tags },
  ];

  const COLORS = ['#10b981', '#ef4444', '#7c3aed'];

  return (
    <div className="p-8 space-y-8">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">Total Tags</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {stats.total_tags.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">Verified Tags</p>
          <p className="text-3xl font-bold text-green-600 mt-2">
            {stats.verified_tags.toLocaleString()}
          </p>
          <p className="text-xs text-gray-600 mt-2">
            {((stats.verified_tags / stats.total_tags) * 100).toFixed(1)}% success rate
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">High Risk</p>
          <p className="text-3xl font-bold text-red-600 mt-2">
            {stats.high_risk_tags.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">Critical</p>
          <p className="text-3xl font-bold text-purple-600 mt-2">
            {stats.critical_tags.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {COLORS.map((color, index) => (
                  <Cell key={`cell-${index}`} fill={color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium text-gray-600">Batch Windows</span>
              <span className="font-semibold">{stats.total_batch_windows}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium text-gray-600">Verification Rate</span>
              <span className="font-semibold">
                {((stats.verified_tags / stats.total_tags) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium text-gray-600">Recent Tags</span>
              <span className="font-semibold">
                {Math.floor(stats.total_tags / 10)}/day avg
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
