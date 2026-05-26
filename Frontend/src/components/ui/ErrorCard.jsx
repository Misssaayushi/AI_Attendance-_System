import React from 'react';
import { ShieldAlert, RefreshCw, CameraOff, WifiOff, FileSearch } from 'lucide-react';
import Card from '../Card';
import Button from '../Button';

const ErrorCard = ({ type = 'general', title, description, onRetry }) => {
  const getIcon = () => {
    switch (type) {
      case 'camera':
        return <CameraOff size={32} className="text-red-400" />;
      case 'network':
        return <WifiOff size={32} className="text-orange-400" />;
      case 'empty':
        return <FileSearch size={32} className="text-yellow-400" />;
      case 'general':
      default:
        return <ShieldAlert size={32} className="text-red-400" />;
    }
  };

  return (
    <Card className="flex flex-col items-center text-center p-8 bg-gray-900/40 border border-gray-800 rounded-2xl max-w-md mx-auto shadow-2xl animate-in zoom-in-95 duration-200">
      <div className="p-4 rounded-full bg-gray-850/50 border border-gray-800/80 mb-4 shadow-inner">
        {getIcon()}
      </div>
      
      <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
        {title || 'System Error Encountered'}
      </h3>
      
      <p className="text-xs text-gray-400 font-medium leading-relaxed mb-6">
        {description || 'The requested action could not be verified. Please check logs and try again.'}
      </p>
      
      {onRetry && (
        <Button 
          onClick={onRetry} 
          className="flex items-center gap-2 text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-xl py-2 px-5 transition-all shadow-lg shadow-blue-500/20"
        >
          <RefreshCw size={14} className="animate-spin-hover" />
          <span>Try Again</span>
        </Button>
      )}
    </Card>
  );
};

export default ErrorCard;
