import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import {
  HiOutlineHome,
  HiOutlineUsers,
  HiOutlineCollection,
  HiOutlineChartBar,
  HiOutlineLogout,
  HiOutlineCog,
  HiOutlineBell,
} from 'react-icons/hi';

const AdminLayout: React.FC = () => {
  const { admin, logoutAdmin } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logoutAdmin();
    navigate('/admin/login');
  };

  const navItems = [
    { to: '/admin/dashboard', label: 'Dashboard', icon: HiOutlineHome },
    { to: '/admin/users', label: 'Users', icon: HiOutlineUsers },
    { to: '/admin/listings', label: 'Listings', icon: HiOutlineCollection },
    { to: '/admin/reports', label: 'Reports', icon: HiOutlineChartBar },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex bg-dark-950">
      {/* Sidebar */}
      <aside className="w-64 bg-dark-900 border-r border-dark-800 fixed h-full">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-dark-800">
            <Link to="/admin/dashboard" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-dark-950 font-bold text-xl">K</span>
              </div>
              <div>
                <span className="font-display font-bold text-lg text-white">KAYAK</span>
                <span className="block text-xs text-gray-500">Admin Panel</span>
              </div>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 py-6 px-3">
            <ul className="space-y-1">
              {navItems.map((item) => (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                      isActive(item.to)
                        ? 'bg-primary-500/20 text-primary-400 shadow-glow/30'
                        : 'text-gray-400 hover:text-white hover:bg-dark-800/50'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          {/* Admin Info */}
          <div className="p-4 border-t border-dark-800">
            <div className="flex items-center space-x-3 p-3 rounded-xl bg-dark-800/50">
              <div className="w-10 h-10 bg-gradient-to-br from-secondary-500 to-accent-purple rounded-full flex items-center justify-center">
                <span className="text-white font-medium">
                  {admin?.first_name?.charAt(0)}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {admin?.first_name} {admin?.last_name}
                </p>
                <p className="text-xs text-gray-500 truncate">{admin?.role}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 w-full mt-3 px-4 py-2 text-gray-400 hover:text-white hover:bg-dark-800/50 rounded-lg transition-colors"
            >
              <HiOutlineLogout className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 ml-64">
        {/* Top Bar */}
        <header className="sticky top-0 z-40 h-16 bg-dark-900/80 backdrop-blur-sm border-b border-dark-800">
          <div className="flex items-center justify-between h-full px-6">
            <h1 className="text-xl font-display font-semibold text-white">
              {navItems.find((item) => isActive(item.to))?.label || 'Admin'}
            </h1>
            <div className="flex items-center space-x-4">
              <button className="relative p-2 text-gray-400 hover:text-white hover:bg-dark-800/50 rounded-lg transition-colors">
                <HiOutlineBell className="w-6 h-6" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
              </button>
              <button className="p-2 text-gray-400 hover:text-white hover:bg-dark-800/50 rounded-lg transition-colors">
                <HiOutlineCog className="w-6 h-6" />
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;


