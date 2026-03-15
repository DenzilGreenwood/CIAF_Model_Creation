import React, { ReactNode } from 'react';
import { Link, useLocation, Outlet, useNavigate } from 'react-router-dom';
import {
  Home,
  CheckCircle2,
  Clock,
  BarChart3,
  Users,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuthStore } from '@/store/auth.store';
import { useState } from 'react';

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      logout();
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Logout failed:', error);
      setIsLoggingOut(false);
    }
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Verify Output', href: '/verify', icon: CheckCircle2 },
    { name: 'Audit Trail', href: '/audit', icon: Clock },
    { name: 'Compliance', href: '/compliance', icon: BarChart3 },
    { name: 'Organization Stats', href: '/stats', icon: BarChart3 },
    { name: 'Agent Registry', href: '/agents', icon: Users },
    { name: 'Admin', href: '/admin', icon: Settings },
  ];

  const isActive = (href: string) => location.pathname === href;

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-slate-900 text-slate-50 transition-all duration-300 overflow-hidden flex flex-col border-r border-slate-800`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-xl font-bold flex items-center gap-2">
              {sidebarOpen ? (
                <>
                  CIAF <span className="text-cyan-400">VAULT</span>
                </>
              ) : (
                'CV'
              )}
            </Link>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 hover:bg-slate-800 rounded transition-colors"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                  active
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-cyan-400'
                }`}
                title={sidebarOpen ? '' : item.name}
              >
                <Icon size={20} />
                {sidebarOpen && <span className="ml-3">{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* User Menu */}
        <div className="p-4 border-t border-slate-800">
          {user && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                {sidebarOpen && (
                  <div className="text-sm">
                    <p className="font-medium text-slate-100">{user.name}</p>
                    <p className="text-xs text-slate-500">{user.role}</p>
                  </div>
                )}
              </div>
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="p-1 hover:bg-slate-800 rounded transition-colors disabled:opacity-50"
                title="Logout"
              >
                <LogOut size={18} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-slate-900 border-b border-slate-800 px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-50">
              CIAF Verification Dashboard
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Cryptographic verification of AI-generated outputs
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-full" />
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
