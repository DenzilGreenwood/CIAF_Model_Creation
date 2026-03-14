import React, { useState, useMemo } from 'react';
import { useVerifyOutputMutation } from '@/api/hooks';
import { VerificationStatusBadge, RiskBadge, PoliciesBadge, LoadingSpinner } from '@/components/common/Badges';
import { useNotifications } from '@/store/notifications.store';
import { Search, Download, Copy, AlertCircle, CheckCircle } from 'lucide-react';

export const VerificationEngine: React.FC = () => {
  const [tagId, setTagId] = useState('');
  const [includeAudit, setIncludeAudit] = useState(true);
  const [searchOrgId, setSearchOrgId] = useState('');
  const [searchRiskLevel, setSearchRiskLevel] = useState<string>('');
  const { mutate: verify, data: result, isPending, error, isError } = useVerifyOutputMutation();
  const notifications = useNotifications();

  const handleVerify = async () => {
    if (!tagId.trim()) {
      notifications.warning('Please enter a tag ID');
      return;
    }

    console.log('[UI] Verifying tag:', tagId);
    verify(tagId, {
      onError: (err) => {
        console.error('[UI] Verification failed:', err);
        const message = err instanceof Error ? err.message : 'Unknown error occurred';
        notifications.error(`Verification failed: ${message}`);
      },
      onSuccess: () => {
        console.log('[UI] Verification succeeded');
        notifications.success('Output verified successfully');
      },
    });
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    notifications.success('Copied to clipboard');
  };

  const handleDownload = () => {
    if (!result) return;
    const json = JSON.stringify(result, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `verification_${result.tag_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Filter results based on search criteria
  const filteredResult = useMemo(() => {
    if (!result) return null;

    let matches = true;
    if (searchOrgId && !result.organization_id.includes(searchOrgId)) {
      matches = false;
    }
    if (searchRiskLevel && result.risk_level !== searchRiskLevel) {
      matches = false;
    }

    return matches ? result : null;
  }, [result, searchOrgId, searchRiskLevel]);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Input Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Verify Output</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tag ID
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={tagId}
                onChange={(e) => setTagId(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleVerify()}
                placeholder="550e8400-e29b-41d4-a716-446655440000"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleVerify}
                disabled={isPending}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                <Search size={18} />
                {isPending ? 'Verifying...' : 'Verify'}
              </button>
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="includeAudit"
              checked={includeAudit}
              onChange={(e) => setIncludeAudit(e.target.checked)}
              className="h-4 w-4 text-blue-600"
            />
            <label htmlFor="includeAudit" className="ml-2 text-sm text-gray-700">
              Include Agent Audit Trail
            </label>
          </div>

          {/* Filter Section */}
          {result && (
            <div className="border-t pt-4 mt-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Filter Results</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Organization ID
                  </label>
                  <input
                    type="text"
                    value={searchOrgId}
                    onChange={(e) => setSearchOrgId(e.target.value)}
                    placeholder="Filter by org..."
                    className="w-full px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Risk Level
                  </label>
                  <select
                    value={searchRiskLevel}
                    onChange={(e) => setSearchRiskLevel(e.target.value)}
                    className="w-full px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Levels</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Type
                  </label>
                  <select
                    className="w-full px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 bg-gray-50"
                    disabled
                  >
                    <option>{result.inference_type.replace('_', ' ')}</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Loading State */}
      {isPending && <LoadingSpinner message="Verifying output..." />}

      {/* Error State */}
      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">Verification Failed</h3>
              <p className="text-sm text-red-700">
                {error instanceof Error ? error.message : 'An unknown error occurred'}
              </p>
              <p className="text-xs text-red-600 mt-2">
                💡 Tip: Make sure the tag ID is valid and exists in the system.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {result && filteredResult && (
        <div className="space-y-6">
          {/* Success Message */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="text-green-600" size={20} />
              <p className="text-sm font-medium text-green-900">
                ✓ Output successfully verified
              </p>
            </div>
          </div>

          {/* Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Verification Result</h3>
              <div className="flex gap-2">
                <button
                  onClick={handleDownload}
                  title="Download verification result as JSON"
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Download size={20} />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <p className="text-sm text-gray-600 mb-2">Status</p>
                <VerificationStatusBadge verified={result.verified} merkleValid={result.merkle_proof_valid} />
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-2">Risk Level</p>
                <RiskBadge level={result.risk_level} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 font-medium">Tag ID</p>
                <div className="flex items-center gap-2 mt-1">
                  <code className="text-sm bg-gray-100 px-2 py-1 rounded flex-1 truncate">
                    {result.tag_id}
                  </code>
                  <button onClick={() => handleCopy(result.tag_id)} className="p-1 hover:bg-gray-100 rounded transition-colors">
                    <Copy size={16} />
                  </button>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 font-medium">Organization</p>
                <p className="mt-1 text-sm font-mono text-blue-600">{result.organization_id}</p>
              </div>
            </div>
          </div>

          {/* Inference Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Inference Details</h4>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 font-medium">Type</p>
                <p className="mt-1 text-sm capitalize bg-blue-50 px-2 py-1 rounded inline-block">
                  {result.inference_type.replace('_', ' ')}
                </p>
              </div>
              {result.model_name && (
                <div>
                  <p className="text-sm text-gray-600 font-medium">Model</p>
                  <p className="mt-1 text-sm">{result.model_name}</p>
                </div>
              )}
            </div>

            {result.agent_ids.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 font-medium mb-2">Agents</p>
                <div className="flex flex-wrap gap-2">
                  {result.agent_ids.map((agentId) => (
                    <span
                      key={agentId}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded text-sm"
                    >
                      {agentId}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Policies */}
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Policies Applied</h4>
            <PoliciesBadge policies={result.policies_applied} maxDisplay={10} />
          </div>

          {/* Merkle Proofs */}
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Cryptographic Proofs</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium text-gray-700">Task Batch Verified</span>
                <span className={`text-sm font-semibold ${result.task_batch_verified ? 'text-green-600' : 'text-red-600'}`}>
                  {result.task_batch_verified ? '✓ Valid' : '✗ Invalid'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium text-gray-700">Org Batch Verified</span>
                <span className={`text-sm font-semibold ${result.org_batch_verified ? 'text-green-600' : 'text-red-600'}`}>
                  {result.org_batch_verified ? '✓ Valid' : '✗ Invalid'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium text-gray-700">Merkle Proof Valid</span>
                <span className={`text-sm font-semibold ${result.merkle_proof_valid ? 'text-green-600' : 'text-red-600'}`}>
                  {result.merkle_proof_valid ? '✓ Valid' : '✗ Invalid'}
                </span>
              </div>
            </div>
          </div>

          {/* Issues & Warnings */}
          {(result.issues.length > 0 || result.warnings.length > 0) && (
            <div className="bg-white rounded-lg shadow p-6">
              <h4 className="font-semibold text-gray-900 mb-4">Issues & Warnings</h4>

              {result.issues.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-red-700 mb-2">Issues:</p>
                  <ul className="space-y-1">
                    {result.issues.map((issue, idx) => (
                      <li key={idx} className="text-sm text-red-600 flex items-start">
                        <span className="mr-2">•</span>
                        {issue}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.warnings.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-yellow-700 mb-2">Warnings:</p>
                  <ul className="space-y-1">
                    {result.warnings.map((warning, idx) => (
                      <li key={idx} className="text-sm text-yellow-600 flex items-start">
                        <span className="mr-2">•</span>
                        {warning}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Audit Trail */}
          {includeAudit && result.agent_audit_trail.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h4 className="font-semibold text-gray-900 mb-4">Agent Audit Trail ({result.agent_audit_trail.length})</h4>
              <div className="space-y-3">
                {result.agent_audit_trail.map((action, idx) => (
                  <div key={idx} className="flex items-start p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{action.agent_id}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        {action.action_type} - {new Date(action.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <RiskBadge level={action.risk_level} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty Audit Trail Message */}
          {includeAudit && result.agent_audit_trail.length === 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-700">
                No audit trail available yet. Full merkle chain validation is in progress.
              </p>
            </div>
          )}
        </div>
      )}

      {/* No Results Message */}
      {result && !filteredResult && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-700">
            No results match your filter criteria. Try adjusting your search filters.
          </p>
        </div>
      )}
    </div>
  );
};
