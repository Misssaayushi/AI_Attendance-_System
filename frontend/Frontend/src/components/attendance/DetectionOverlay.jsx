import React from 'react';

const colorMap = {
  marked: {
    border: 'border-green-500/80',
    bg: 'bg-green-500/10',
    corner: 'border-green-400',
    dot: 'bg-green-500',
    text: 'text-green-400',
    label: 'Marked ✓',
  },
  duplicate: {
    border: 'border-orange-500/80',
    bg: 'bg-orange-500/10',
    corner: 'border-orange-400',
    dot: 'bg-orange-500',
    text: 'text-orange-400',
    label: 'Already Marked',
  },
  unrecognized: {
    border: 'border-red-500/80',
    bg: 'bg-red-500/10',
    corner: 'border-red-400',
    dot: 'bg-red-500',
    text: 'text-red-400',
    label: 'Unknown',
  },
};

const DetectionOverlay = ({ isScanning, trackingBox, trackingBoxes }) => {
  const getBoxStyle = (box) => {
    if (!box) return {};
    const [top, right, bottom, left] = box;
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

  // Multi-face mode: render a box for each detected face
  const hasMultiBoxes = Array.isArray(trackingBoxes) && trackingBoxes.length > 0;

  return (
    <div className="absolute inset-0 pointer-events-none z-10">
      {/* Scanning Line */}
      {isScanning && !trackingBox && !hasMultiBoxes && (
        <div className="absolute inset-x-0 h-0.5 bg-blue-400 shadow-[0_0_15px_rgba(96,165,250,0.8)] animate-scan z-20"></div>
      )}

      {/* Multi-face bounding boxes */}
      {isScanning && hasMultiBoxes && (
        <div className="absolute inset-0">
          {trackingBoxes.map((item, idx) => {
            if (!item.box) return null;
            const colors = colorMap[item.type] || colorMap.unrecognized;
            return (
              <div
                key={idx}
                className={`border-2 ${colors.border} ${colors.bg} rounded-lg`}
                style={getBoxStyle(item.box)}
              >
                {/* Corner Brackets */}
                <div className={`absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 ${colors.corner}`}></div>
                <div className={`absolute -top-1 -right-1 w-4 h-4 border-t-2 border-r-2 ${colors.corner}`}></div>
                <div className={`absolute -bottom-1 -left-1 w-4 h-4 border-b-2 border-l-2 ${colors.corner}`}></div>
                <div className={`absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 ${colors.corner}`}></div>
                
                {/* Label */}
                <div className={`absolute -top-6 left-0 text-[10px] uppercase font-bold tracking-widest ${colors.text} flex items-center gap-1 bg-black/60 px-1.5 py-0.5 rounded whitespace-nowrap`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${colors.dot} animate-ping`}></span>
                  {item.name || colors.label}
                </div>

                {/* Tick for marked */}
                {item.type === 'marked' && (
                  <div className="absolute inset-0 flex items-center justify-center animate-in zoom-in duration-300">
                    <div className="bg-white rounded-full p-1 shadow-[0_0_30px_rgba(34,197,94,0.8)]">
                      <svg className="w-10 h-10 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Single-face Real Face Detection Box (backward compat) */}
      {isScanning && trackingBox && !hasMultiBoxes && (
        <div className="absolute inset-0">
          <div 
            className="border-2 border-blue-500/80 bg-blue-500/10 rounded-lg animate-pulse"
            style={getBoxStyle(trackingBox)}
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
