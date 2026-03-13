import React, { useState } from 'react';
import { useComplianceReport } from '@/api/hooks';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { LoadingSpinner } from '@/components/common/Badges';

export const ComplianceDashboard: React.FC = () => {
  const [selectedOrg, setSelectedOrg] = useState('healthcare_org_001');
  const [selectedPolicy, setSelectedPolicy] = useState<string | undefined>();

  const { data: compliance, isLoading } = useComplianceReport(selectedOrg, selectedPolicy);

  const complianceData = compliance
    ? [
        {
          name: compliance.policy,
          covered: compliance.policy_covered,
          total: compliance.total_outputs,
          rate: (compliance.compliance_rate * 100).toFixed(1),
        },
      ]
    : [];

  const policies = [
    'HIPAA_COMPLIANT',
    'FDA_SaMD',
    'ISO_14971',
    '   FAIR_LENDING_COMPLIANCE',
    'SR_11_7_MODEL_VALIDATION',
    'ECOA_TRANSPARENCY',
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Organization
            </label>
            <select
              value={selectedOrg}
              onChange={(e) => setSelectedOrg(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="healthcare_org_001">Healthcare Org</option>
              <option value="banking_org_001">Banking Org</option>
              <option value="government_org_001">Government Org</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Policy
            </label>
            <select
              value={selectedPolicy || ''}
              onChange={(e) => setSelectedPolicy(e.target.value || undefined)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Policies</option>
              {policies.map((policy) => (
                <option key={policy} value={policy}>
                  {policy}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner message="Loading compliance data..." />
      ) : compliance ? (
        <div className="space-y-6">
          {/* Compliance Metrics */}
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Compliance Rate</p>
              <p className="text-4xl font-bold text-green-600 mt-2">
                {(compliance.compliance_rate * 100).toFixed(1)}%
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Policy Covered Outputs</p>
              <p className="text-4xl font-bold text-blue-600 mt-2">
                {compliance.policy_covered.toLocaleString()}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">Total Outputs</p>
              <p className="text-4xl font-bold text-purple-600 mt-2">
                {compliance.total_outputs.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Compliance Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Overview</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={complianceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="covered" fill="#10b981" name="Policy Covered" />
                <Bar dataKey="total" fill="#e5e7eb" name="Total" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Compliance Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Policy Details</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
                <div>
                  <p className="font-medium text-gray-900">{compliance.policy}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {compliance.policy_covered} of {compliance.total_outputs} outputs compliant
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">
                    {(compliance.compliance_rate * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-600 mt-1">Compliance Rate</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-blue-50 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">Recommendations</h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="mr-3">•</span>
                <span>
                  Current compliance rate is excellent. Continue monitoring policy enforcement.
                </span>
              </li>
              <li className="flex items-start">
                <span className="mr-3">•</span>
                <span>
                  Review non-compliant outputs from the past 30 days to identify patterns.
                </span>
              </li>
              <li className="flex items-start">
                <span className="mr-3">•</span>
                <span>
                  Consider implementing automated alerts for compliance violations.
                </span>
              </li>
            </ul>
          </div>
        </div>
      ) : null}
    </div>
  );
};
