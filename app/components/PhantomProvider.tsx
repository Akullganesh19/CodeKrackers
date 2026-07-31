'use client';

import { useEffect, useRef } from 'react';

export function PhantomProvider({ children }: { children: React.ReactNode }) {
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current || (window as any).__initialized) return;
    initialized.current = true;
    (window as any).__initialized = true;

    const originalFetch = window.fetch;
    const inFlightRequests = new Map<string, Promise<Response>>();

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      // Safely extract URL and method
      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;
      const method = (init?.method || (input instanceof Request ? input.method : 'GET')).toUpperCase();

      // Robust header extraction
      const initHeaders = new Headers(init?.headers);
      const inputHeaders = input instanceof Request ? input.headers : new Headers();

      // Bypass next.js internal requests
      const isNextInternal =
        initHeaders.has('RSC') || initHeaders.has('Next-Router-Prefetch') ||
        inputHeaders.has('RSC') || inputHeaders.has('Next-Router-Prefetch');

      // Bypass if cache is no-store or it's not a GET request
      if (isNextInternal || method !== 'GET' || init?.cache === 'no-store') {
        return originalFetch(input, init);
      }

      // Request Coalescing key
      const authHeader = initHeaders.get('Authorization') || inputHeaders.get('Authorization') || '';
      const cacheKey = `${method}:${url}:${authHeader}`;

      // In-flight deduplication
      if (inFlightRequests.has(cacheKey)) {
        console.debug(`[Phantom] Coalesced request: ${url}`);
        const promise = inFlightRequests.get(cacheKey)!;
        // Clone the response so multiple awaiters don't consume the same body stream
        const response = await promise;
        return response.clone();
      }

      const fetchPromise = originalFetch(input, init).finally(() => {
        inFlightRequests.delete(cacheKey);
      });

      inFlightRequests.set(cacheKey, fetchPromise);

      const response = await fetchPromise;
      return response.clone();
    };

    return () => {
      // Cleanup for HMR
      if (process.env.NODE_ENV === 'development') {
        window.fetch = originalFetch;
        (window as any).__initialized = false;
      }
    };
  }, []);

  return <>{children}</>;
}
