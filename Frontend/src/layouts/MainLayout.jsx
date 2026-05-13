import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { LayoutDashboard, Users, UserPlus, ClipboardList } from 'lucide-react';

const MainLayout = () => {
  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-gray-800 border-r border-gray-700 hidden md:flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold text-white tracking-wider">AI AttendSys</h2>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/dashboard" className="flex items-center space-x-3 text-gray-300 hover:text-white hover:bg-gray-700 px-3 py-2 rounded-md transition-colors">
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </Link>
          <Link to="/attendance" className="flex items-center space-x-3 text-gray-300 hover:text-white hover:bg-gray-700 px-3 py-2 rounded-md transition-colors">
            <Users size={20} />
            <span>Live Attendance</span>
          </Link>
          <Link to="/records" className="flex items-center space-x-3 text-gray-300 hover:text-white hover:bg-gray-700 px-3 py-2 rounded-md transition-colors">
            <ClipboardList size={20} />
            <span>Records</span>
          </Link>
          <Link to="/register" className="flex items-center space-x-3 text-gray-300 hover:text-white hover:bg-gray-700 px-3 py-2 rounded-md transition-colors">
            <UserPlus size={20} />
            <span>Register User</span>
          </Link>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        {/* Mobile Header (placeholder for hamburger menu) */}
        <header className="md:hidden bg-gray-800 border-b border-gray-700 p-4">
          <h2 className="text-xl font-bold">AI AttendSys</h2>
        </header>

        <div className="p-6 md:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
