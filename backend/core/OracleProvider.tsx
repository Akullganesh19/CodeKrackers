'use client';

import React, { useEffect } from 'react';
import { initializeOracle, predictFetch } from './PredictionEngine';
import { usePathname } from 'next/navigation';

export function OracleProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Initialize fetch interceptor synchronously if possible
  if (typeof window !== 'undefined') {
    initializeOracle();
  }

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Instead of hardcoding localhost, construct based on current window location
    // assuming API is hosted on port 8000 on the same hostname by default
    // unless NEXT_PUBLIC_API_URL is defined.
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;
    const summaryUrl = `${apiBaseUrl}/api/analytics/dashboard-summary`;

    // Behavioral Prediction:
    // When a user lands on the dashboard, they predictably interact with threats
    // or request summary analytics immediately. We pre-compute this before they ask.
    if (pathname === '/dashboard') {
      const token = localStorage.getItem('vsdp_token') || 'dummy_token';
      predictFetch(summaryUrl, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
    }

    // When on login, predict they will successfully login and need dashboard data
    if (pathname === '/' || pathname === '/login') {
        const token = localStorage.getItem('vsdp_token');
        if (token) {
            predictFetch(summaryUrl, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
        }
    }

  }, [pathname]);

  return <>{children}</>;
}
