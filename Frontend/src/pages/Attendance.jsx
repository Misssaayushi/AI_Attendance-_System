import React from 'react';
import Card from '../components/Card';
import { Camera } from 'lucide-react';

const Attendance = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Live Attendance</h1>
        <p className="text-gray-400">Real-time facial recognition and attendance tracking.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Camera Feed Placeholder */}
        <Card className="lg:col-span-2 min-h-[400px] flex flex-col items-center justify-center border-gray-700 border-2 bg-black relative">
           <Camera size={48} className="text-gray-600 mb-4" />
           <p className="text-gray-500">Video Feed Offline</p>
           {/* Overlay HUD placeholder */}
           <div className="absolute top-4 right-4 bg-gray-900/80 px-3 py-1 rounded text-xs text-green-400 border border-green-500/30">
              System Active
           </div>
        </Card>

        {/* Live Recognition Log */}
        <Card className="flex flex-col max-h-[500px]">
          <h3 className="font-semibold text-lg border-b border-gray-700 pb-3 mb-3">Recent Recognitions</h3>
          <div className="flex-1 overflow-y-auto space-y-3">
             {/* Placeholder entries */}
             <div className="bg-gray-700/50 p-3 rounded-md flex items-center justify-between">
                <div>
                   <p className="font-medium text-sm text-white">Alice Smith</p>
                   <p className="text-xs text-gray-400">ID: 90210</p>
                </div>
                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">09:01 AM</span>
             </div>
             <div className="bg-gray-700/50 p-3 rounded-md flex items-center justify-between">
                <div>
                   <p className="font-medium text-sm text-white">Bob Jones</p>
                   <p className="text-xs text-gray-400">ID: 90211</p>
                </div>
                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">09:05 AM</span>
             </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Attendance;
