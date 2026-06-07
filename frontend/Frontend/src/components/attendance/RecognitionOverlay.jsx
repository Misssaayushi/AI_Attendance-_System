import React from 'react';

const RecognitionOverlay = ({ isScanning }) => {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Corner Borders */}
      <div className="absolute top-8 left-8 w-12 h-12 border-t-4 border-l-4 border-blue-500 rounded-tl-lg"></div>
      <div className="absolute top-8 right-8 w-12 h-12 border-t-4 border-r-4 border-blue-500 rounded-tr-lg"></div>
      <div className="absolute bottom-8 left-8 w-12 h-12 border-b-4 border-l-4 border-blue-500 rounded-bl-lg"></div>
      <div className="absolute bottom-8 right-8 w-12 h-12 border-b-4 border-r-4 border-blue-500 rounded-br-lg"></div>

      {/* Scanning Line */}
      {isScanning && (
        <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent shadow-[0_0_15px_rgba(59,130,246,0.5)] animate-scan"></div>
      )}

      {/* HUD Details */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-4">
        <div className="bg-gray-900/60 backdrop-blur-md px-3 py-1 rounded border border-blue-500/30 text-[10px] uppercase tracking-widest text-blue-400 font-bold">
          Face Tracking Active
        </div>
        <div className="bg-gray-900/60 backdrop-blur-md px-3 py-1 rounded border border-blue-500/30 text-[10px] uppercase tracking-widest text-blue-400 font-bold">
          98.2% Confidence
        </div>
      </div>
    </div>
  );
};

export default RecognitionOverlay;
