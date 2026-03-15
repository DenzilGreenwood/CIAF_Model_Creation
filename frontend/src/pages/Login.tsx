import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormData } from '@/types/auth-validation';
import { useAuthStore } from '@/store/auth.store';
import { apiClient } from '@/api/client';
import { Eye, EyeOff, Mail, Lock, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login: authLogin } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const rememberMe = watch('rememberMe');

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setServerError(null);

    try {
      // Call API login endpoint
      const response = await apiClient.login(data.email, data.password);

      // Store tokens and user info
      authLogin(
        response.user,
        response.access_token,
        response.refresh_token
      );

      setSuccess(true);

      // Redirect to originally requested page or dashboard
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      setTimeout(() => {
        navigate(from);
      }, 500);
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 401) {
        setServerError('Invalid email or password');
      } else if (error.response?.status === 422) {
        setServerError('Please check your input and try again');
      } else if (error.message === 'Network Error') {
        setServerError('Unable to connect to the server. Please try again.');
      } else {
        setServerError(error.response?.data?.detail || 'Login failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl" />
      </div>

      {/* Login Card */}
      <div className="relative w-full max-w-md">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg shadow-2xl p-8 backdrop-blur-sm">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="inline-block mb-4 p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
              <Lock className="text-cyan-400" size={32} />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
            <p className="text-slate-400">Sign in to your AI-EI account</p>
          </div>

          {/* Server Error Alert */}
          {serverError && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex gap-3">
              <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="font-medium text-red-400">Login Failed</p>
                <p className="text-sm text-red-300 mt-1">{serverError}</p>
              </div>
            </div>
          )}

          {/* Success Alert */}
          {success && (
            <div className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg flex gap-3">
              <CheckCircle2 className="text-green-400 flex-shrink-0 mt-0.5" size={20} />
              <p className="text-green-400">Login successful! Redirecting...</p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email Field */}
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
                <p className="text-sm text-red-400 mt-1.5 flex items-center gap-1">
                  <AlertCircle size={16} />
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" size={20} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  {...register('password')}
                  className={`w-full pl-10 pr-10 py-2.5 bg-slate-700/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition ${
                    errors.password ? 'border-red-500' : 'border-slate-600'
                  }`}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-slate-300 transition"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-sm text-red-400 mt-1.5 flex items-center gap-1">
                  <AlertCircle size={16} />
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="rememberMe"
                {...register('rememberMe')}
                className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-cyan-500 cursor-pointer"
                disabled={isLoading}
              />
              <label htmlFor="rememberMe" className="ml-2 text-sm text-slate-400 cursor-pointer">
                Remember me for 30 days
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || success}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-medium rounded-lg transition flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center gap-4">
            <div className="flex-1 h-px bg-slate-700" />
            <span className="text-sm text-slate-500">or</span>
            <div className="flex-1 h-px bg-slate-700" />
          </div>

          {/* Footer Links */}
          <div className="space-y-3 text-sm">
            <div className="text-center text-slate-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-cyan-400 hover:text-cyan-300 font-medium transition">
                Sign up
              </Link>
            </div>
            <div className="text-center">
              <Link to="/forgot-password" className="text-cyan-400 hover:text-cyan-300 font-medium transition">
                Forgot password?
              </Link>
            </div>
          </div>

          {/* Demo Info */}
          <div className="mt-6 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-300">
            <p className="font-medium mb-1">Demo Credentials:</p>
            <p>Email: demo@ciaf.io</p>
            <p>Password: DemoPass123!</p>
          </div>
        </div>

        {/* Terms */}
        <p className="text-center text-xs text-slate-500 mt-4">
          By signing in, you agree to our{' '}
          <Link to="/terms" className="text-cyan-400 hover:text-cyan-300">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link to="/privacy" className="text-cyan-400 hover:text-cyan-300">
            Privacy Policy
          </Link>
        </p>
      </div>
    </div>
  );
};
