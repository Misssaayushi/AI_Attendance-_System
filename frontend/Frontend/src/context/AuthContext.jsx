import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginAdmin, getMe, logoutAdmin } from '../services/api';
import { extractData } from '../services/apiHelpers';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'));
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Validate the existing token on mount
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await getMe();
        if (response.data && response.data.success) {
          const data = extractData(response);
          setUser({ username: data.username, id: data.id });
          setIsAuthenticated(true);
        } else {
          // If response success is false
          logout();
        }
      } catch (error) {
        console.error('Failed to validate token on mount:', error);
        logout(); // Token expired/invalid
      } finally {
        setIsLoading(false);
      }
    };

    validateToken();
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await loginAdmin(username, password);
      const data = extractData(response) || response.data;
      const { access_token, username: userVal } = data;
      
      localStorage.setItem('auth_token', access_token);
      setToken(access_token);
      setUser({ username: userVal });
      setIsAuthenticated(true);
      return data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      // Best effort backend notification (optional for stateless JWT)
      if (token) {
        await logoutAdmin().catch(() => {});
      }
    } finally {
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider value={{ token, user, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
