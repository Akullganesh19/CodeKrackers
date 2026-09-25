'use client';

import React from 'react';

// Request coalescing map
const inFlightRequests = new Map<string, Promise<Response>>();

// Extend window interface safely for HMR (Hot Module Replacement) flag
declare global {
  interface Window {
    __phantomFetchInitialized?: boolean;
  }
}

if (typeof window !== 'undefined' && !window.__phantomFetchInitialized) {
  const originalFetch = window.fetch;

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    let requestMethod = 'GET';
    let urlStr = '';

    if (input instanceof Request) {
      requestMethod = (input.method || 'GET').toUpperCase();
      urlStr = input.url;
    } else {
      requestMethod = (init?.method || 'GET').toUpperCase();
      urlStr = input.toString();
    }

    // Only coalesce GET requests
    if (requestMethod !== 'GET') {
      return originalFetch(input, init);
    }

    // We use the token to differentiate states if auth changes, preventing leakages
    let token = 'anonymous';
    try {
      token = localStorage.getItem('vsdp_token') || 'anonymous';
    } catch (e) {
      // Ignore security errors in strict mode where localStorage might be blocked
    }
    const cacheKey = `${requestMethod}:${urlStr}:${token}`;

    if (inFlightRequests.has(cacheKey)) {
      console.debug(`[Phantom 🌀] Coalesced request: ${urlStr}`);
      const response = await inFlightRequests.get(cacheKey)!;
      // We MUST clone the response because the body stream can only be read once per response instance
      return response.clone();
    }

    const fetchPromise = originalFetch(input, init)
      .then(response => {
        // Remove from in-flight map immediately upon resolution
        inFlightRequests.delete(cacheKey);
        return response;
      })
      .catch(err => {
        inFlightRequests.delete(cacheKey);
        throw err;
      });

    inFlightRequests.set(cacheKey, fetchPromise);

    const resolvedResponse = await fetchPromise;
    return resolvedResponse.clone();
  };

  window.__phantomFetchInitialized = true;
  console.log('[Phantom 🌀] Global fetch coalescing initialized');
}

export default function FetchInterceptor({ children }: { children?: React.ReactNode }) {
  // It initializes synchronously in module scope on the client side
  return <>{children}</>;
}
