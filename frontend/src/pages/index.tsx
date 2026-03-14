import React from 'react';

// Stub pages
export const AuditTrailViewer: React.FC = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Audit Trail Viewer</h1>
    <div className="bg-white rounded-lg shadow p-6">
      <p className="text-gray-600">Search and filter agent audit trails by tag ID, agent, or date range.</p>
      <div className="mt-6 space-y-4">
        <input
          type="text"
          placeholder="Search tag ID or agent..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-600">
          Enter a tag ID to view agent audit trail
        </div>
      </div>
    </div>
  </div>
);

export const AgentRegistry: React.FC = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Agent Registry</h1>
    <div className="bg-white rounded-lg shadow p-6">
      <p className="text-gray-600 mb-4">View all registered agents with their policies and metrics.</p>
      <div className="space-y-3">
        {['healthcare_reader_001', 'analysis_agent_001', 'recommendation_agent_001'].map((agent) => (
          <div key={agent} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">{agent}</p>
              <p className="text-xs text-gray-600 mt-1">Status: Active</p>
            </div>
            <button className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  </div>
);

export const AdminPanel: React.FC = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Admin Panel</h1>
    <div className="grid grid-cols-2 gap-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Cache Management</h3>
        <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Refresh Cache
        </button>
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="space-y-2 text-sm">
          <div>Database: <span className="text-green-600 font-medium">Connected</span></div>
          <div>Cache: <span className="text-green-600 font-medium">Healthy</span></div>
          <div>API: <span className="text-green-600 font-medium">Running</span></div>
        </div>
      </div>
    </div>
  </div>
);

export const NotFound: React.FC = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-50">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-900">404</h1>
      <p className="text-gray-600 mt-2">Page not found</p>
    </div>
  </div>
);
