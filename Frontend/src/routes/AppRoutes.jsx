import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Layouts
import MainLayout from '../layouts/MainLayout';

// Pages
import Register from '../pages/Register';
import Attendance from '../pages/Attendance';
import Dashboard from '../pages/Dashboard';
import Records from '../pages/Records';
import SYNEXIntro from '../components/intro/SYNEXIntro';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0a0c] flex flex-col items-center justify-center select-none relative overflow-hidden">
        <div className="absolute w-[300px] h-[300px] bg-cyan-500/10 blur-[80px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
        <div className="relative z-10 flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin"></div>
          <span className="font-mono text-[9px] text-cyan-400 tracking-[3px] uppercase animate-pulse">Checking Permissions...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<SYNEXIntro />} />
      <Route path="/register" element={<Register />} />
      <Route path="/attendance" element={<Attendance />} />
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/records" element={<Records />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
