'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { getDecodedToken, isTokenExpired, logout as logoutUtil } from '@/backend/core/auth-utils';

interface AuthContextType {
  user: any | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const syncAuthState = () => {
    if (!isTokenExpired()) {
      setUser(getDecodedToken());
    } else {
      setUser(null);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    setTimeout(syncAuthState, 0);
    // Sync state across tabs if one tab logs out
    window.addEventListener('storage', syncAuthState);
    return () => window.removeEventListener('storage', syncAuthState);
  }, []);

  const login = (token: string) => {
    localStorage.setItem('vsdp_token', token);
    // Set cookie for middleware access (valid for 7 days)
    document.cookie = `vsdp_token=${token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Strict; Secure`;
    setUser(getDecodedToken());
  };

  const logout = () => {
    logoutUtil();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};