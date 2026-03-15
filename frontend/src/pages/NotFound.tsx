import React from 'react';
import { Home, Search, AlertCircle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export const NotFound: React.FC = () => {
  const suggestions = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/dashboard', label: 'Dashboard', icon: Search },
    { path: '/verification', label: 'Verification Engine', icon: AlertCircle },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-lg w-full text-center space-y-8">
        {/* 404 Error */}
        <div className="space-y-4">
          <div className="text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
            404
          </div>
          <h1 className="text-4xl font-bold text-white">Page Not Found</h1>
          <p className="text-lg text-slate-400">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        {/* Illustration */}
        <div className="flex justify-center">
          <div className="relative w-40 h-40">
            {/* Outer circle */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 blur-xl" />

            {/* Inner circle with icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-slate-800/50 border border-slate-700 rounded-full p-8">
                <AlertCircle size={64} className="text-cyan-400" strokeWidth={1.5} />
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-4">
          <Link
            to="/"
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition"
          >
            <ArrowLeft size={20} />
            Go Back Home
          </Link>

          <button
            onClick={() => window.history.back()}
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition"
          >
            <ArrowLeft size={20} />
            Go to Previous Page
          </button>
        </div>

        {/* Suggestions */}
        <div className="space-y-3">
          <p className="text-sm text-slate-500 uppercase tracking-wide font-medium">Popular Pages</p>
          <div className="grid grid-cols-3 gap-3">
            {suggestions.map((suggestion) => {
              const Icon = suggestion.icon;
              return (
                <Link
                  key={suggestion.path}
                  to={suggestion.path}
                  className="flex flex-col items-center gap-2 p-3 bg-slate-800/50 border border-slate-700 rounded-lg hover:bg-slate-800 hover:border-slate-600 transition"
                >
                  <Icon size={24} className="text-cyan-400" />
                  <span className="text-xs font-medium text-slate-300">{suggestion.label}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Help Text */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <p className="text-sm text-slate-400">
            If you think this is an error, please <span className="text-cyan-400 hover:text-cyan-300 cursor-pointer">contact support</span> or check the{' '}
            <span className="text-cyan-400 hover:text-cyan-300 cursor-pointer">documentation</span>.
          </p>
        </div>

        {/* Status Code */}
        <div className="pt-4 border-t border-slate-700">
          <code className="text-xs text-slate-500 font-mono">HTTP 404 · Not Found</code>
        </div>
      </div>
    </div>
  );
};
