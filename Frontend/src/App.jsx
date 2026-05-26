import React, { useState } from 'react';
import AppRoutes from './routes/AppRoutes';
import SYNEXIntro from './components/intro/SYNEXIntro';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';

/**
 * App.jsx
 * =========================================================================
 * Root entry point of the React Application.
 */
function App() {
  const [showSplash, setShowSplash] = useState(true);

  // Triggered when the user successfully authenticates and enters the system
  const handleEnterDashboard = () => {
    setShowSplash(false);
  };

  return (
    <ThemeProvider>
      <ToastProvider>
        {showSplash ? (
          <SYNEXIntro onEnter={handleEnterDashboard} />
        ) : (
          <AppRoutes />
        )}
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
