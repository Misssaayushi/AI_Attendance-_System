import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, 
  Users, 
  UserPlus, 
  ClipboardList, 
  ChevronLeft, 
  ChevronRight, 
  FileText,
  LogOut,
  Settings
} from 'lucide-react';

const Sidebar = ({ isCollapsed, toggleCollapse, isMobileOpen, closeMobile }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={20} /> },
    { name: 'Records', path: '/records', icon: <ClipboardList size={20} /> },
    { name: 'Students', path: '/students', icon: <Users size={20} /> },
    { name: 'Reports', path: '/reports', icon: <FileText size={20} />, optional: true }
  ];

  const sidebarClasses = `
    fixed inset-y-0 left-0 z-40 bg-gray-900 border-r border-gray-800 flex flex-col transition-all duration-300 ease-in-out
    ${isCollapsed ? 'w-20' : 'w-64'}
    ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
    md:relative md:translate-x-0
  `;

  const linkClasses = ({ isActive }) => `
    flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group relative overflow-hidden
    ${isActive 
      ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20 font-semibold' 
      : 'text-gray-400 hover:text-white hover:bg-gray-800/60 border border-transparent'}
  `;

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={closeMobile}
        />
      )}

      <aside className={sidebarClasses}>
        {/* Sidebar Header */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-gray-800/80">
          <div className="flex items-center space-x-3 overflow-hidden">
            {!isCollapsed && (
              <span className="text-white font-extrabold tracking-wider text-base whitespace-nowrap bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-300">
                AttendSys
              </span>
            )}
          </div>
          
          {/* Collapse toggle (Desktop only) */}
          <button 
            onClick={toggleCollapse}
            className="hidden md:flex items-center justify-center p-1.5 rounded-lg bg-gray-800/60 hover:bg-gray-800 border border-gray-700/50 text-gray-400 hover:text-white transition-colors"
          >
            {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Sidebar Navigation */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {menuItems.map((item) => (
            <NavLink 
              key={item.path} 
              to={item.path}
              onClick={closeMobile}
              className={linkClasses}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-blue-500 rounded-r-md shadow-[0_0_8px_#3b82f6]" />
                  )}
                  <div className="flex-shrink-0 transition-transform group-hover:scale-110 duration-200">
                    {item.icon}
                  </div>
                  
                  {!isCollapsed && (
                    <span className="text-sm tracking-wide transition-opacity duration-200">
                      {item.name}
                    </span>
                  )}

                  {/* Tooltip for collapsed mode */}
                  {isCollapsed && (
                    <div className="absolute left-full ml-4 px-2.5 py-1.5 bg-gray-950 text-xs font-semibold text-white rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 shadow-xl border border-gray-800 whitespace-nowrap">
                      {item.name}
                    </div>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-800/80 space-y-1.5">
          <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/60 border border-transparent transition-colors group relative">
            <Settings size={20} className="flex-shrink-0" />
            {!isCollapsed && <span className="text-sm font-medium">Settings</span>}
            {isCollapsed && (
              <div className="absolute left-full ml-4 px-2.5 py-1.5 bg-gray-950 text-xs font-semibold text-white rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 border border-gray-800 whitespace-nowrap">
                Settings
              </div>
            )}
          </button>
          
          <button 
            onClick={async () => {
              await logout();
              navigate('/');
            }}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-red-400 hover:text-red-300 hover:bg-red-500/10 border border-transparent transition-colors group relative cursor-pointer text-left"
          >
            <LogOut size={20} className="flex-shrink-0" />
            {!isCollapsed && <span className="text-sm font-medium">Exit Terminal</span>}
            {isCollapsed && (
              <div className="absolute left-full ml-4 px-2.5 py-1.5 bg-red-950 text-xs font-semibold text-red-200 rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 border border-red-900 whitespace-nowrap">
                Exit Terminal
              </div>
            )}
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
