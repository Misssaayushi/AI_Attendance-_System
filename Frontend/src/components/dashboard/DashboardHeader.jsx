import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Bell, User, Clock, ChevronDown, Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';

const DashboardHeader = ({ toggleMobileSidebar }) => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();
  const location = useLocation();
  const [time, setTime] = useState(new Date());

  const getInitials = () => {
    if (!user?.username) return 'AD';
    const parts = user.username.split(/[._\s-]/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return user.username.slice(0, 2).toUpperCase();
  };

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/dashboard': return 'Dashboard Overview';
      case '/attendance': return 'Live Attendance scan';
      case '/records': return 'Attendance Database';
      case '/register': return 'New Face Enrollment';
      default: return 'Admin Console';
    }
  };

  const getPageDesc = () => {
    switch (location.pathname) {
      case '/dashboard': return 'Real-time analytics, daily metrics, and system status.';
      case '/attendance': return 'Biometric camera scanning and live matching feed.';
      case '/records': return 'Search, filter, and review attendance logs.';
      case '/register': return 'Enroll new student profiles with live facial biometrics.';
      default: return 'AI Attendance Management System.';
    }
  };

  const formattedDate = time.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  return (
    <header className="h-16 flex items-center justify-between px-6 bg-gray-900 border-b border-gray-800/80 sticky top-0 z-30">
      {/* Title / Hamburger */}
      <div className="flex items-center space-x-4">
        <button 
          onClick={toggleMobileSidebar}
          className="p-2 -ml-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none md:hidden transition-colors"
        >
          <Menu size={20} />
        </button>
        
        <div className="hidden sm:block">
          <h1 className="text-lg font-bold text-white tracking-wide leading-none">{getPageTitle()}</h1>
          <p className="text-[11px] text-gray-500 mt-1 font-medium">{getPageDesc()}</p>
        </div>
      </div>

      {/* Actions (Notifications, Live Clock, Profile) */}
      <div className="flex items-center space-x-4">
        {/* Live Clock Widget */}
        <div className="hidden lg:flex items-center space-x-2.5 px-3 py-1.5 bg-gray-800/50 rounded-xl border border-gray-800/80 text-gray-400">
          <Clock size={14} className="text-blue-500 animate-pulse" />
          <span className="text-xs font-semibold tracking-wide font-mono">
            {formattedDate} — {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
        </div>

        {/* Theme Toggle Button */}
        <button 
          onClick={toggleTheme}
          className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-850 border border-transparent hover:border-gray-800/50 transition-all cursor-pointer"
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {theme === 'dark' ? <Sun size={18} className="text-yellow-500" /> : <Moon size={18} className="text-blue-500" />}
        </button>

        {/* Notifications Button */}
        <button className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-850 border border-transparent hover:border-gray-800/50 transition-all relative">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full ring-2 ring-gray-900"></span>
        </button>

        {/* Divider */}
        <div className="h-6 w-px bg-gray-800"></div>

        {/* Profile Dropdown */}
        <div className="flex items-center space-x-2.5 cursor-pointer group">
          <div className="w-8 h-8 rounded-xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400 font-bold text-sm shadow-inner group-hover:bg-blue-600/20 transition-all">
            {getInitials()}
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-bold text-gray-300 group-hover:text-white transition-colors leading-none">{user?.username || 'Admin Profile'}</p>
            <p className="text-[9px] text-gray-500 mt-0.5 uppercase tracking-wider font-extrabold">Super Administrator</p>
          </div>
          <ChevronDown size={14} className="text-gray-500 group-hover:text-gray-300 transition-colors" />
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
