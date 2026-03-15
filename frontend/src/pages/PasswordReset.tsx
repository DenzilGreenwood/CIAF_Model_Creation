import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { passwordResetSchema, passwordResetConfirmSchema } from '@/types/auth-validation';
import { apiClient } from '@/api/client';
import { Mail, Lock, ArrowLeft, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export const ForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(passwordResetSchema),
    defaultValues: {
      email: '',
    },
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);

    try {
      await apiClient.requestPasswordReset(data.email);
      setSubmitted(true);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center p-4">
        <div className="relative w-full max-w-md">
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg shadow-2xl p-8 backdrop-blur-sm text-center">
            <div className="inline-block mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
              <CheckCircle2 className="text-green-400" size={40} />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Check Your Email</h1>
            <p className="text-slate-400 mb-6">
              We've sent a password reset link to your email. Click the link to create a new password.
            </p>
            <p className="text-sm text-slate-500 mb-6">
              The link expires in 1 hour for security reasons.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg transition"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center p-4">
      <div className="relative w-full max-w-md">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg shadow-2xl p-8 backdrop-blur-sm">
          {/* Back Button */}
          <Link
            to="/login"
            className="inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 mb-6 transition"
          >
            <ArrowLeft size={20} />
            Back to Login
          </Link>

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Reset Password</h1>
            <p className="text-slate-400">Enter your email to receive a password reset link</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex gap-3">
              <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" size={20} />
                <input
                  type="email"
                  placeholder="you@example.com"
                  {...register('email')}
                  className={`w-full pl-10 pr-4 py-2.5 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition ${
                    errors.email ? 'border-red-500' : 'border-slate-600'
                  }`}
                  disabled={isLoading}
                />
              </div>
              {errors.email && (
                <p className="text-sm text-red-400 mt-1.5">{errors.email.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-medium rounded-lg transition flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Sending...
                </>
              ) : (
                'Send Reset Link'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// ============================================================
// Password Reset Confirmation Page
// ============================================================

export const ResetPassword: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm({
    resolver: zodResolver(passwordResetConfirmSchema),
    defaultValues: {
      token: token || '',
      password: '',
      confirmPassword: '',
    },
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center p-4">
        <div className="relative w-full max-w-md">
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg shadow-2xl p-8 backdrop-blur-sm text-center">
            <div className="inline-block mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <AlertCircle className="text-red-400" size={40} />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Invalid Link</h1>
            <p className="text-slate-400 mb-6">This password reset link is invalid or has expired.</p>
            <Link
              to="/forgot-password"
              className="inline-block py-2.5 px-6 bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg transition"
            >
              Request New Link
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);

    try {
      await apiClient.confirmPasswordReset(token, data.password);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to reset password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center p-4">
        <div className="relative w-full max-w-md">
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg shadow-2xl p-8 backdrop-blur-sm text-center">
            <div className="inline-block mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
              <CheckCircle2 className="text-green-400" size={40} />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Password Reset Successful</h1>
            <p className="text-slate-400">Your password has been reset. Redirecting to login...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center p-4">
      <div className="relative w-full max-w-md">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg shadow-2xl p-8 backdrop-blur-sm">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Create New Password</h1>
            <p className="text-slate-400">Enter your new password below</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex gap-3">
              <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="At least 8 characters"
                {...register('password')}
                className={`w-full px-4 py-2.5 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition ${
                  errors.password ? 'border-red-500' : 'border-slate-600'
                }`}
                disabled={isLoading}
              />
              {errors.password && (
                <p className="text-sm text-red-400 mt-1.5">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Confirm Password</label>
              <input
                type={showConfirm ? 'text' : 'password'}
                placeholder="Confirm password"
                {...register('confirmPassword')}
                className={`w-full px-4 py-2.5 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition ${
                  errors.confirmPassword ? 'border-red-500' : 'border-slate-600'
                }`}
                disabled={isLoading}
              />
              {errors.confirmPassword && (
                <p className="text-sm text-red-400 mt-1.5">{errors.confirmPassword.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-medium rounded-lg transition flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Resetting...
                </>
              ) : (
                'Reset Password'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
