import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now() + Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, message, type }]);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      removeToast(id);
    }, 4000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      
      {/* Toast Notification Container */}
      <div className="fixed bottom-5 right-5 z-[9999] flex flex-col gap-3 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => {
          const config = getToastConfig(toast.type);
          return (
            <div 
              key={toast.id}
              className={`flex items-center gap-3 p-4 rounded-xl border shadow-2xl transition-all duration-350 pointer-events-auto animate-in slide-in-from-bottom-5 fade-in duration-300 ${config.bg} ${config.border} ${config.text}`}
            >
              <div className="flex-shrink-0">
                {config.icon}
              </div>
              <p className="text-xs font-semibold flex-1 leading-snug">{toast.message}</p>
              <button 
                onClick={() => removeToast(toast.id)}
                className="p-1 rounded-lg hover:bg-black/10 transition-colors text-current opacity-70 hover:opacity-100"
              >
                <X size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

const getToastConfig = (type) => {
  switch (type) {
    case 'error':
      return {
        icon: <XCircle size={16} />,
        bg: 'bg-red-500/10 backdrop-blur-md',
        border: 'border-red-500/20',
        text: 'text-red-400'
      };
    case 'warning':
      return {
        icon: <AlertTriangle size={16} />,
        bg: 'bg-orange-500/10 backdrop-blur-md',
        border: 'border-orange-500/20',
        text: 'text-orange-400'
      };
    case 'info':
      return {
        icon: <Info size={16} />,
        bg: 'bg-blue-500/10 backdrop-blur-md',
        border: 'border-blue-500/20',
        text: 'text-blue-400'
      };
    case 'success':
    default:
      return {
        icon: <CheckCircle size={16} />,
        bg: 'bg-green-500/10 backdrop-blur-md',
        border: 'border-green-500/20',
        text: 'text-green-400'
      };
  }
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
