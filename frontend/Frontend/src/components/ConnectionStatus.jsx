import { useState, useEffect } from 'react';
import { getHealthStatus } from '../services/api';

const ConnectionStatus = () => {
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const check = async () => {
      try {
        await getHealthStatus();
        setIsConnected(true);
      } catch {
        setIsConnected(false);
      }
    };

    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  if (isConnected) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-[9999] bg-red-600 text-white text-center py-2 text-sm font-medium shadow-md animate-slideDown">
      ⚠️ Cannot connect to Backend server. Some features may be unavailable.
    </div>
  );
};

export default ConnectionStatus;
