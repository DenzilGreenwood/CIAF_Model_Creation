import React from 'react';
import { RiskLevel, VerificationStatus } from '@/types';
import { CheckCircle2, XCircle, AlertCircle, Clock } from 'lucide-react';

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, className = '' }) => {
  const styles: Record<RiskLevel, string> = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
    critical: 'bg-purple-100 text-purple-800',
  };

  const labels: Record<RiskLevel, string> = {
    low: 'Low Risk',
    medium: 'Medium Risk',
    high: 'High Risk',
    critical: 'Critical Risk',
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${styles[level]} ${className}`}>
      {labels[level]}
    </span>
  );
};

interface VerificationStatusBadgeProps {
  verified: boolean;
  merkleValid?: boolean;
  className?: string;
}

export const VerificationStatusBadge: React.FC<VerificationStatusBadgeProps> = ({
  verified,
  merkleValid = true,
  className = '',
}) => {
  if (verified && merkleValid) {
    return (
      <div className={`flex items-center space-x-2 text-green-700 ${className}`}>
        <CheckCircle2 size={20} />
        <span className="font-medium">Verified</span>
      </div>
    );
  }

  if (!verified) {
    return (
      <div className={`flex items-center space-x-2 text-red-700 ${className}`}>
        <XCircle size={20} />
        <span className="font-medium">Unverified</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-2 text-yellow-700 ${className}`}>
      <AlertCircle size={20} />
      <span className="font-medium">Warning</span>
    </div>
  );
};

interface PoliciesBadgeProps {
  policies: string[];
  maxDisplay?: number;
}

export const PoliciesBadge: React.FC<PoliciesBadgeProps> = ({ policies, maxDisplay = 3 }) => {
  const displayed = policies.slice(0, maxDisplay);
  const remaining = policies.length - maxDisplay;

  return (
    <div className="flex flex-wrap gap-2">
      {displayed.map((policy) => (
        <span
          key={policy}
          className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
        >
          {policy}
        </span>
      ))}
      {remaining > 0 && (
        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
          +{remaining} more
        </span>
      )}
    </div>
  );
};

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', message }) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`${sizeMap[size]} animate-spin`}>
        <Clock className="text-blue-600" />
      </div>
      {message && <p className="mt-4 text-gray-600">{message}</p>}
    </div>
  );
};
