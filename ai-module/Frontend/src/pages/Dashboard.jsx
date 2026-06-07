import React from 'react';
import Card from '../components/Card';
import { Users, Clock, AlertTriangle } from 'lucide-react';

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard Overview</h1>
        <p className="text-gray-400">Daily statistics and system status.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="flex items-center space-x-4">
          <div className="p-3 bg-blue-500/20 text-blue-400 rounded-full">
            <Users size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-400 font-medium">Total Present</p>
            <p className="text-2xl font-bold text-white">124</p>
          </div>
        </Card>
        
        <Card className="flex items-center space-x-4">
          <div className="p-3 bg-green-500/20 text-green-400 rounded-full">
            <Clock size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-400 font-medium">On Time</p>
            <p className="text-2xl font-bold text-white">110</p>
          </div>
        </Card>

        <Card className="flex items-center space-x-4">
          <div className="p-3 bg-yellow-500/20 text-yellow-400 rounded-full">
            <AlertTriangle size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-400 font-medium">Late Arrivals</p>
            <p className="text-2xl font-bold text-white">14</p>
          </div>
        </Card>
      </div>

      <Card className="min-h-[300px] flex items-center justify-center border-dashed">
         <p className="text-gray-500">Chart.js Implementation Placeholder (Phase 3)</p>
      </Card>
    </div>
  );
};

export default Dashboard;
