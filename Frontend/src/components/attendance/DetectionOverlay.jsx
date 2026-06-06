import React from 'react';

const DetectionOverlay = ({ isScanning, trackingBox }) => {
  const getBoxStyle = () => {
    if (!trackingBox || !isScanning) return {};
    const [top, right, bottom, left] = trackingBox;
    const width = right - left;
    const height = bottom - top;
    
    return {
      top: `${(top / 720) * 100}%`,
      left: `${(left / 1280) * 100}%`,
      width: `${(width / 1280) * 100}%`,
      height: `${(height / 720) * 100}%`,
      position: 'absolute'
    };
  };

  return (
    <div className="absolute inset-0 pointer-events-none z-10">
      {/* Scanning Line */}
      {isScanning && !trackingBox && (
        <div className="absolute inset-x-0 h-0.5 bg-blue-400 shadow-[0_0_15px_rgba(96,165,250,0.8)] animate-scan z-20"></div>
      )}

      {/* Real Face Detection Box */}
      {isScanning && trackingBox && (
        <div className="absolute inset-0">
          <div 
            className="border-2 border-blue-500/80 bg-blue-500/10 rounded-lg animate-pulse"
            style={getBoxStyle()}
          >
            {/* Corner Brackets */}
            <div className="absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 border-green-400"></div>
            <div className="absolute -top-1 -right-1 w-4 h-4 border-t-2 border-r-2 border-green-400"></div>
            <div className="absolute -bottom-1 -left-1 w-4 h-4 border-b-2 border-l-2 border-green-400"></div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 border-green-400"></div>
            
            {/* Tracking Text */}
            <div className="absolute -top-6 left-0 text-[10px] uppercase font-bold tracking-widest text-green-400 flex items-center gap-1 bg-black/50 px-1 rounded">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-ping"></span>
              Attendance Marked
            </div>

            {/* Big Green Tick */}
            <div className="absolute inset-0 flex items-center justify-center animate-in zoom-in duration-300">
              <div className="bg-white rounded-full p-1 shadow-[0_0_30px_rgba(34,197,94,0.8)]">
                <svg className="w-16 h-16 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* HUD Info Labels */}
      <div className="absolute top-6 left-6 space-y-2">
        <div className="bg-gray-900/60 backdrop-blur-md px-2 py-1 rounded border border-white/10 text-[9px] uppercase tracking-tighter text-gray-300">
          Sensor: Active
        </div>
      </div>
    </div>
  );
};

export default DetectionOverlay;
