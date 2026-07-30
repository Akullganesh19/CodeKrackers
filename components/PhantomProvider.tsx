'use client';

import { useEffect } from 'react';

export function PhantomProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    if ((window as any).__phantomInitialized) return;
    (window as any).__phantomInitialized = true;

    const originalFetch = window.fetch;
    const inFlight = new Map<string, Promise<Response>>();

    window.fetch = function (input: RequestInfo | URL, init?: RequestInit) {
      // Safely extract the URL
      const url = typeof input === 'string'
        ? input
        : input instanceof URL
          ? input.toString()
          : input.url;

      // Safely extract the method
      const method = (init?.method || (input instanceof Request ? input.method : 'GET')).toUpperCase();

      // Check headers to bypass RSC / Prefetch
      const headers = new Headers(init?.headers || (input instanceof Request ? input.headers : {}));

      const isRSC = headers.has('RSC');
      const isPrefetch = headers.has('Next-Router-Prefetch');
      const isNoStore = init?.cache === 'no-store';
      const isGet = method === 'GET';

      // Bypass custom caching for internal/Next.js requests or non-GETs
      if (!isGet || isRSC || isPrefetch || isNoStore) {
        return originalFetch(input, init);
      }

      const cacheKey = `${method}:${url}`;

      if (inFlight.has(cacheKey)) {
        const promise = inFlight.get(cacheKey)!;
        return promise.then(res => res.clone());
      }

      const fetchPromise = originalFetch(input, init);

      const sharedPromise = fetchPromise.finally(() => {
        inFlight.delete(cacheKey);
      });

      inFlight.set(cacheKey, sharedPromise);

      return sharedPromise.then(res => res.clone());
    };
  }, []);

  return <>{children}</>;
}
