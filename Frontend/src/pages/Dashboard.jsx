import React, { useState, useEffect } from 'react';
import { Users, UserCheck, UserX, Percent } from 'lucide-react';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import StatCard from '../components/dashboard/StatCard';
import AttendanceCharts from '../components/dashboard/AttendanceCharts';
import StudentTable from '../components/dashboard/StudentTable';
import { getDashboardStats } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalStudents: 150,
    presentToday: 128,
    absentToday: 22,
    attendancePercentage: '85.3%'
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getDashboardStats();
        const data = response.data;
        setStats({
          totalStudents: data.totalStudents || 150,
          presentToday: data.totalPresent || 128,
          absentToday: (data.totalStudents - data.totalPresent) || 22,
          attendancePercentage: `${((data.totalPresent / data.totalStudents) * 100).toFixed(1)}%`
        });
      } catch (error) {
        console.log("Using mock dashboard stats (backend not yet connected)");
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="space-y-8">
      {/* 4 Analytics Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in duration-500">
        <StatCard 
          title="Total Students" 
          value={stats.totalStudents} 
          icon={<Users size={22} />} 
          color="blue"
          trend="+5 new this week"
          trendType="up"
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
          trend="-2 from yesterday"
          trendType="down"
        />
        <StatCard 
          title="Attendance Rate" 
          value={stats.attendancePercentage} 
          icon={<Percent size={22} />} 
          color="purple"
          trend="+1.2% average"
          trendType="up"
        />
      </div>

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
