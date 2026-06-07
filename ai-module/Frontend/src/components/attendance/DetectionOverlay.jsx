import React from 'react';

const DetectionOverlay = ({ isScanning }) => {
  return (
    <div className="absolute inset-0 pointer-events-none z-10">
      {/* Scanning Line */}
      {isScanning && (
        <div className="absolute inset-x-0 h-0.5 bg-blue-400 shadow-[0_0_15px_rgba(96,165,250,0.8)] animate-scan z-20"></div>
      )}

      {/* Pulsing Face Detection Box */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className={`w-64 h-80 border-2 border-blue-500/40 rounded-lg relative ${isScanning ? 'animate-pulse' : ''}`}>
          {/* Corner Brackets */}
          <div className="absolute -top-1 -left-1 w-6 h-6 border-t-4 border-l-4 border-blue-500"></div>
          <div className="absolute -top-1 -right-1 w-6 h-6 border-t-4 border-r-4 border-blue-500"></div>
          <div className="absolute -bottom-1 -left-1 w-6 h-6 border-b-4 border-l-4 border-blue-500"></div>
          <div className="absolute -bottom-1 -right-1 w-6 h-6 border-b-4 border-r-4 border-blue-500"></div>
          
          {/* Tracking Text */}
          <div className="absolute -top-8 left-0 text-[10px] uppercase font-bold tracking-widest text-blue-400 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping"></span>
            Face Tracking Active
          </div>
        </div>
      </div>

      {/* HUD Info Labels */}
      <div className="absolute top-6 left-6 space-y-2">
        <div className="bg-gray-900/60 backdrop-blur-md px-2 py-1 rounded border border-white/10 text-[9px] uppercase tracking-tighter text-gray-300">
          Sensor: Cam-01 [User_Mode]
        </div>
        <div className="bg-gray-900/60 backdrop-blur-md px-2 py-1 rounded border border-white/10 text-[9px] uppercase tracking-tighter text-gray-300">
          FPS: 30.2
        </div>
      </div>
    </div>
  );
};

export default DetectionOverlay;
