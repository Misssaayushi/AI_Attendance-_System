import React from 'react';
import { X, AlertCircle, CheckCircle, Info } from 'lucide-react';

const Alert = ({ variant = 'info', message, onClose }) => {
  const styles = {
    info: "bg-blue-500/10 border-blue-500/50 text-blue-400",
    success: "bg-green-500/10 border-green-500/50 text-green-400",
    error: "bg-red-500/10 border-red-500/50 text-red-400",
    warning: "bg-yellow-500/10 border-yellow-500/50 text-yellow-400"
  };

  const icons = {
    info: <Info size={20} />,
    success: <CheckCircle size={20} />,
    error: <AlertCircle size={20} />,
    warning: <AlertCircle size={20} />
  };

  return (
    <div className={`flex items-center justify-between p-4 mb-6 border rounded-lg animate-in fade-in slide-in-from-top-4 duration-300 ${styles[variant]}`}>
      <div className="flex items-center space-x-3">
        {icons[variant]}
        <span className="text-sm font-medium">{message}</span>
      </div>
      {onClose && (
        <button onClick={onClose} className="hover:opacity-70 transition-opacity">
          <X size={20} />
        </button>
      )}
    </div>
  );
};

export default Alert;
