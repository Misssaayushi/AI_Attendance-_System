import React from 'react';

const SkeletonLoader = ({ variant = 'card', count = 1 }) => {
  const renderSkeleton = () => {
    switch (variant) {
      case 'table':
        return (
          <div className="w-full space-y-4 p-5 animate-pulse bg-gray-900/40 rounded-xl border border-gray-800">
            <div className="flex justify-between items-center pb-2">
              <div className="h-4 bg-gray-800 rounded w-1/4"></div>
              <div className="h-8 bg-gray-800 rounded w-1/3"></div>
            </div>
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex gap-4 items-center">
                  <div className="h-8 bg-gray-800 rounded-lg w-8 flex-shrink-0"></div>
                  <div className="h-4 bg-gray-800 rounded flex-1"></div>
                  <div className="h-4 bg-gray-800 rounded w-1/4"></div>
                  <div className="h-4 bg-gray-800 rounded w-12"></div>
                </div>
              ))}
            </div>
          </div>
        );
      case 'webcam':
        return (
          <div className="relative aspect-video w-full rounded-2xl bg-gray-950/80 border border-gray-800 overflow-hidden flex flex-col items-center justify-center space-y-3 animate-pulse">
            <div className="w-12 h-12 rounded-full border-4 border-gray-800 border-t-blue-500 animate-spin"></div>
            <div className="h-3 bg-gray-800 rounded w-1/3"></div>
          </div>
        );
      case 'list':
        return (
          <div className="space-y-3 p-5 bg-gray-900/40 rounded-xl border border-gray-800 animate-pulse">
            <div className="h-4 bg-gray-800 rounded w-1/3 mb-4"></div>
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-gray-800 flex-shrink-0"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-3 bg-gray-800 rounded w-1/2"></div>
                  <div className="h-2 bg-gray-800 rounded w-1/3"></div>
                </div>
              </div>
            ))}
          </div>
        );
      case 'card':
      default:
        return (
          <div className="p-6 bg-gray-900/40 border border-gray-800 rounded-2xl space-y-4 animate-pulse flex items-center justify-between">
            <div className="space-y-2.5 flex-1">
              <div className="h-3 bg-gray-800 rounded w-1/3"></div>
              <div className="h-8 bg-gray-800 rounded w-1/2"></div>
              <div className="h-3 bg-gray-800 rounded w-1/4"></div>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gray-800"></div>
          </div>
        );
    }
  };

  return (
    <div className="grid grid-cols-1 gap-6 w-full">
      {[...Array(count)].map((_, index) => (
        <React.Fragment key={index}>
          {renderSkeleton()}
        </React.Fragment>
      ))}
    </div>
  );
};

export default SkeletonLoader;
