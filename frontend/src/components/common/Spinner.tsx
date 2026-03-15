import React from 'react';
import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  message?: string;
  fullScreen?: boolean;
  overlay?: boolean;
}

const sizeMap = {
  sm: { icon: 16, container: 'p-4' },
  md: { icon: 32, container: 'p-8' },
  lg: { icon: 48, container: 'p-12' },
  xl: { icon: 64, container: 'p-16' },
};

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', message, fullScreen = false, overlay = false }) => {
  const spinnerContent = (
    <div className={`flex flex-col items-center justify-center ${sizeMap[size].container}`}>
      <div className="relative">
        {/* Outer glow */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 opacity-10 blur-xl animate-pulse" />

        {/* Spinner icon */}
        <Loader2 size={sizeMap[size].icon} className="text-cyan-400 animate-spin relative z-10" strokeWidth={1.5} />
      </div>

      {/* Message */}
      {message && (
        <p className="mt-4 text-slate-300 text-center animate-pulse">{message}</p>
      )}
    </div>
  );

  // Full screen overlay spinner
  if (fullScreen) {
    return (
      <div className={`fixed inset-0 flex items-center justify-center ${overlay ? 'bg-black/50 backdrop-blur-sm' : 'bg-slate-950'} z-50`}>
        {spinnerContent}
      </div>
    );
  }

  // Regular spinner
  return spinnerContent;
};

/**
 * Deprecated: Use Spinner component instead
 * Kept for backward compatibility
 */
export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; message?: string }> = ({ size = 'md', message }) => (
  <Spinner size={size} message={message} />
);
