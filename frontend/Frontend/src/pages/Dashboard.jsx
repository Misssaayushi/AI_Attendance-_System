import React, { useState, useEffect } from 'react';
import { Users, UserCheck, UserX, Percent } from 'lucide-react';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import StatCard from '../components/dashboard/StatCard';
import AttendanceCharts from '../components/dashboard/AttendanceCharts';
import StudentTable from '../components/dashboard/StudentTable';
import { getDashboardSummary } from '../services/api';
import { extractData } from '../services/apiHelpers';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await getDashboardSummary();
      const data = extractData(response);
      
      setStats({
        totalStudents: data.total_students || 0,
        presentToday: data.present_count || 0,
        absentToday: data.absent_count || 0,
        lateToday: data.late_count || 0,
        attendancePercentage: `${(data.attendance_percentage || 0).toFixed(1)}%`,
      });
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8">
      {/* 4 Analytics Summary Cards */}
      {isLoading && !stats ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-800/50 rounded-2xl border border-gray-700/30" />
          ))}
        </div>
      ) : error && !stats ? (
        <div className="text-center py-12">
          <p className="text-red-400">{error}</p>
          <button onClick={fetchDashboardData} className="mt-4 text-blue-400 hover:text-blue-300">
            Retry
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in duration-500">
          <StatCard 
            title="Total Students" 
            value={stats.totalStudents} 
            icon={<Users size={22} />} 
            color="blue"
            trend="Active enrolled"
            trendType="neutral"
          />
          <StatCard 
            title="Present Today" 
            value={stats.presentToday} 
            icon={<UserCheck size={22} />} 
            color="green"
            trend="Live tracking"
            trendType="neutral"
          />
          <StatCard 
            title="Absent Today" 
            value={stats.absentToday} 
            icon={<UserX size={22} />} 
            color="red"
            trend="Not marked"
            trendType="neutral"
          />
          <StatCard 
            title="Attendance Rate" 
            value={stats.attendancePercentage} 
            icon={<Percent size={22} />} 
            color="purple"
            trend="Overall average"
            trendType="neutral"
          />
        </div>
      )}

      {/* Chart Section */}
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
        <AttendanceCharts />
      </div>

      {/* Bottom Section: Student Attendance Table & Live Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
        <div className="lg:col-span-2">
          <StudentTable />
        </div>
        <div className="lg:col-span-1">
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
