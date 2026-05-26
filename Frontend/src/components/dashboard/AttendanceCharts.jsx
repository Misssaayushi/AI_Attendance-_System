import React from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import Card from '../Card';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const AttendanceCharts = () => {
  // Common Dark Theme Options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#9ca3af',
          font: { family: 'Inter, sans-serif', size: 11, weight: '500' },
          boxWidth: 10,
          boxHeight: 10,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#f3f4f6',
        bodyColor: '#d1d5db',
        borderColor: '#374151',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        displayColors: true,
        boxPadding: 4
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(55, 65, 81, 0.3)', drawBorder: false },
        ticks: { color: '#9ca3af', font: { family: 'Inter, sans-serif', size: 10 } }
      },
      y: {
        grid: { color: 'rgba(55, 65, 81, 0.3)', drawBorder: false },
        ticks: { color: '#9ca3af', font: { family: 'Inter, sans-serif', size: 10 } }
      }
    }
  };

  // 1. Line Chart Data (Weekly Trend)
  const lineData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Attendance %',
        data: [82, 85, 88, 84, 86, 90, 85],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: '#3b82f6',
        pointHoverRadius: 7
      }
    ]
  };

  // 2. Bar Chart Data (Monthly present vs absent overview)
  const barData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Present Rate (%)',
        data: [88, 91, 85, 87, 90, 89],
        backgroundColor: '#10b981',
        borderRadius: 6,
        borderWidth: 0,
        barPercentage: 0.6
      },
      {
        label: 'Absent Rate (%)',
        data: [12, 9, 15, 13, 10, 11],
        backgroundColor: '#ef4444',
        borderRadius: 6,
        borderWidth: 0,
        barPercentage: 0.6
      }
    ]
  };

  // 3. Doughnut Chart Data (Department wise distribution)
  const doughnutData = {
    labels: ['CS', 'IT', 'ME', 'EE'],
    datasets: [
      {
        data: [92, 88, 79, 83],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(16, 185, 129, 0.8)'
        ],
        borderColor: '#111827',
        borderWidth: 2,
        hoverOffset: 6
      }
    ]
  };

  const doughnutOptions = {
    ...chartOptions,
    scales: {
      x: { display: false },
      y: { display: false }
    },
    plugins: {
      ...chartOptions.plugins,
      legend: {
        position: 'bottom',
        labels: {
          color: '#9ca3af',
          font: { family: 'Inter, sans-serif', size: 10, weight: '500' },
          boxWidth: 8,
          boxHeight: 8,
          usePointStyle: true
        }
      }
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Line Chart */}
      <Card className="lg:col-span-2 p-5 bg-gray-900/50 border border-gray-800/80">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide uppercase">Weekly Attendance Trend</h3>
            <p className="text-[10px] text-gray-500 mt-0.5">Average weekly scanning performance</p>
          </div>
          <span className="text-xs px-2.5 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-lg font-bold font-mono">
            +3.1% avg
          </span>
        </div>
        <div className="h-64">
          <Line data={lineData} options={chartOptions} />
        </div>
      </Card>

      {/* Doughnut Chart */}
      <Card className="p-5 bg-gray-900/50 border border-gray-800/80">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide uppercase">Department-wise Rate</h3>
            <p className="text-[10px] text-gray-500 mt-0.5">Daily enrollment percentages</p>
          </div>
          <span className="text-xs px-2.5 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-lg font-bold font-mono">
            4 Sectors
          </span>
        </div>
        <div className="h-64 flex items-center justify-center">
          <Doughnut data={doughnutData} options={doughnutOptions} />
        </div>
      </Card>

      {/* Bar Chart */}
      <Card className="lg:col-span-3 p-5 bg-gray-900/50 border border-gray-800/80">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide uppercase">Monthly Attendance Overview</h3>
            <p className="text-[10px] text-gray-500 mt-0.5">Present vs Absent ratio comparison</p>
          </div>
          <span className="text-xs px-2.5 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded-lg font-bold font-mono">
            H1 Overview
          </span>
        </div>
        <div className="h-64">
          <Bar data={barData} options={chartOptions} />
        </div>
      </Card>
    </div>
  );
};

export default AttendanceCharts;
