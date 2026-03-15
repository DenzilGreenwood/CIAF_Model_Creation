import React, { useState, useMemo } from 'react';
import { Search, Filter, Calendar, Clock, CheckCircle2, AlertCircle, AlertTriangle } from 'lucide-react';
import { Spinner } from '@/components/common/Spinner';
import { RiskBadge } from '@/components/common/Badges';
import { useAuditTrailEntries } from '@/api/hooks';
import { useAuthStore } from '@/store/auth.store';

interface AuditEntry {
  entry_id: string;
  action: string;
  timestamp: string;
  result: string;
  actor?: string;
  proof_id?: string;
  organization_id: string;
  details: Record<string, any>;
}

const ACTIONS = [
  'All Actions',
  'submit_proof',
  'verify_proof',
  'generate_certificate',
  'query_audit_trail',
  'get_organization',
];

const RESULT_COLORS = {
  success: 'text-green-500',
  failure: 'text-red-500',
  pending: 'text-yellow-500',
};

const RESULT_BG = {
  success: 'bg-green-50',
  failure: 'bg-red-50',
  pending: 'bg-yellow-50',
};

export const AuditTrailViewer: React.FC = () => {
  // Auth
  const { user } = useAuthStore();
  const organizationId = user?.organization_id || '';

  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAction, setSelectedAction] = useState('All Actions');
  const [dateRange, setDateRange] = useState<'all' | '24h' | '7d' | '30d'>('all');
  const [expandedEntry, setExpandedEntry] = useState<string | null>(null);

  // Fetch audit trail data from API
  const { data: auditData, isLoading, isError, error } = useAuditTrailEntries(
    organizationId,
    {
      limit: 100,
    }
  );

  const auditEntries = auditData?.entries || [];

  // Filter data
  const filteredData = useMemo(() => {
    return auditEntries.filter((entry) => {
      // Filter by action
      if (selectedAction !== 'All Actions' && entry.action !== selectedAction) {
        return false;
      }

      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          entry.entry_id?.toLowerCase().includes(query) ||
          entry.action?.toLowerCase().includes(query) ||
          entry.actor?.toLowerCase().includes(query)
        );
      }

      // Filter by date range
      const entryDate = new Date(entry.timestamp);
      const now = new Date();

      switch (dateRange) {
        case '24h':
          return (now.getTime() - entryDate.getTime()) <= 24 * 60 * 60 * 1000;
        case '7d':
          return (now.getTime() - entryDate.getTime()) <= 7 * 24 * 60 * 60 * 1000;
        case '30d':
          return (now.getTime() - entryDate.getTime()) <= 30 * 24 * 60 * 60 * 1000;
        default:
          return true;
      }
    });
  }, [searchQuery, selectedAction, dateRange, auditEntries]);

  const timeUntilNow = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <div className="space-y-6 p-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-50 mb-2">Audit Trail</h1>
        <p className="text-slate-400">View immutable audit logs of all vault operations</p>
      </div>

      {/* Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-3 text-slate-400" size={20} />
          <input
            type="text"
            placeholder="Search by entry ID, action, proof ID, or actor..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
          />
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Action Filter */}
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Action Type</label>
            <select
              value={selectedAction}
              onChange={(e) => setSelectedAction(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
            >
              {ACTIONS.map((action) => (
                <option key={action} value={action}>
                  {action === 'All Actions' ? action : action.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Date Range Filter */}
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Time Range</label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
            >
              <option value="all">All Time</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
        </div>

        {/* Results Count */}
        <div className="text-sm text-slate-400">
          {isLoading ? (
            <span>Loading audit trail...</span>
          ) : isError ? (
            <span className="text-red-400">Error loading audit trail</span>
          ) : (
            <>
              Showing <span className="text-cyan-400 font-bold">{filteredData.length}</span> of{' '}
              <span className="font-bold">{auditData?.total || 0}</span> entries
            </>
          )}
        </div>
      </div>

      {/* Audit Entries */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-center py-12">
            <Spinner message="Loading audit trail..." />
          </div>
        ) : isError ? (
          <div className="text-center py-12">
            <AlertTriangle className="mx-auto text-red-600 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-slate-400 mb-2">Failed to load audit trail</h3>
            <p className="text-slate-500">{error?.message || 'Please try again or check your connection'}</p>
          </div>
        ) : filteredData.length > 0 ? (
          filteredData.map((entry) => (
            <div
              key={entry.entry_id}
              className={`border rounded-lg transition-all ${
                expandedEntry === entry.entry_id
                  ? 'bg-slate-800 border-cyan-400'
                  : 'bg-slate-900 border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Entry Header */}
              <button
                onClick={() =>
                  setExpandedEntry(expandedEntry === entry.entry_id ? null : entry.entry_id)
                }
                className="w-full p-4 flex items-center justify-between text-left hover:bg-slate-800/50 transition"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  {/* Status Icon */}
                  <div>
                    {entry.result === 'success' ? (
                      <CheckCircle2 className="text-green-500" size={24} />
                    ) : (
                      <AlertCircle className="text-red-500" size={24} />
                    )}
                  </div>

                  {/* Entry Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1 flex-wrap">
                      <span className="font-mono text-sm text-slate-400">{entry.entry_id}</span>
                      <span className="px-2 py-1 bg-slate-800 rounded text-xs font-medium text-cyan-400">
                        {entry.action.replace(/_/g, ' ')}
                      </span>
                      <span
                        className={`text-xs font-medium ${
                          entry.result === 'success' ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {entry.result.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-slate-500">
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {timeUntilNow(entry.timestamp)}
                      </span>
                      {entry.actor && (
                        <span className="font-mono text-xs">{entry.actor}</span>
                      )}
                      {entry.proof_id && (
                        <span className="font-mono text-xs text-slate-400">
                          {entry.proof_id}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Expand Icon */}
                <div className="ml-4">
                  <span
                    className={`text-slate-400 transition-transform ${
                      expandedEntry === entry.entry_id ? 'rotate-180' : ''
                    }`}
                  >
                    ▼
                  </span>
                </div>
              </button>

              {/* Entry Details (Expanded) */}
              {expandedEntry === entry.entry_id && (
                <div className="border-t border-slate-700 p-4 bg-slate-950">
                  <div className="space-y-4">
                    {/* Timeline */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Timestamp
                        </p>
                        <p className="text-sm font-mono text-slate-300">
                          {new Date(entry.timestamp).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Entry ID
                        </p>
                        <p className="text-sm font-mono text-slate-300">{entry.entry_id}</p>
                      </div>
                    </div>

                    {/* Meta Information */}
                    <div className="grid grid-cols-2 gap-4">
                      {entry.organization_id && (
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                            Organization
                          </p>
                          <p className="text-sm font-mono text-slate-300">
                            {entry.organization_id}
                          </p>
                        </div>
                      )}
                      {entry.actor && (
                        <div>
                          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                            Actor
                          </p>
                          <p className="text-sm font-mono text-slate-300">{entry.actor}</p>
                        </div>
                      )}
                    </div>

                    {/* Proof Reference */}
                    {entry.proof_id && (
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">
                          Proof ID
                        </p>
                        <p className="text-sm font-mono text-cyan-400">{entry.proof_id}</p>
                      </div>
                    )}

                    {/* Details JSON */}
                    {Object.keys(entry.details).length > 0 && (
                      <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">
                          Details
                        </p>
                        <pre className="bg-slate-900 rounded p-3 text-xs text-slate-300 overflow-auto max-h-48">
                          {JSON.stringify(entry.details, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <Filter className="mx-auto text-slate-600 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-slate-400 mb-2">No entries found</h3>
            <p className="text-slate-500">Try adjusting your filters or search terms</p>
          </div>
        )}
      </div>

 
    </div>
  );
};

export default AuditTrailViewer;
