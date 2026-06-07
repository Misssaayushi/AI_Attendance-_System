import React from 'react';
import { CheckCircle, AlertCircle, Loader, UserX } from 'lucide-react';

const StatusPanel = ({ state, student }) => {
  const configs = {
    idle: {
      color: 'bg-gray-800/50',
      icon: <Loader className="text-gray-500 animate-spin" />,
      title: 'System Ready',
      desc: 'Waiting for face detection...'
    },
    scanning: {
      color: 'bg-blue-600/20 border-blue-500/50',
      icon: <Loader className="text-blue-500 animate-spin" />,
      title: 'Scanning Face...',
      desc: 'Processing biometric data...'
    },
    success: {
      color: 'bg-green-600/20 border-green-500/50',
      icon: <CheckCircle className="text-green-500" />,
      title: 'Attendance Marked',
      desc: `Welcome back, ${student?.name || 'Student'}`
    },
    duplicate: {
      color: 'bg-orange-600/20 border-orange-500/50',
      icon: <AlertCircle className="text-orange-500" />,
      title: 'Already Marked',
      desc: 'Attendance already recorded for today.'
    },
    unknown: {
      color: 'bg-red-600/20 border-red-500/50',
      icon: <UserX className="text-red-500" />,
      title: 'Unknown Person',
      desc: 'Face not recognized in database.'
    }
  };

  const current = configs[state] || configs.idle;

  return (
    <div className={`p-6 rounded-xl border-2 transition-all duration-500 flex items-center space-x-4 ${current.color} backdrop-blur-md`}>
      <div className="p-3 bg-gray-900/50 rounded-full">
        {React.cloneElement(current.icon, { size: 32 })}
      </div>
      <div>
        <h3 className="text-lg font-bold text-white tracking-tight">{current.title}</h3>
        <p className="text-sm text-gray-400">{current.desc}</p>
        {state === 'success' && student && (
          <p className="text-[10px] text-green-400/70 font-mono mt-1 uppercase">ID: {student.id} | Time: {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
        )}
      </div>
    </div>
  );
};

export default StatusPanel;
