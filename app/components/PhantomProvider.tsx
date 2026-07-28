'use client';

import { useEffect } from 'react';

export default function PhantomProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if ((window as any).__phantomInitialized) return;
    (window as any).__phantomInitialized = true;

    const originalFetch = window.fetch;
    const inFlight = new Map<string, Promise<Response>>();

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      // Safely extract URL and method without consuming body streams
      const url = typeof input === 'string'
        ? input
        : input instanceof URL
          ? input.toString()
          : input.url;

      const method = (init?.method || (input instanceof Request ? input.method : 'GET')).toUpperCase();

      // Check headers safely
      const getHeader = (name: string) => {
        if (init?.headers) {
          if (init.headers instanceof Headers) {
            return init.headers.get(name);
          }
          if (Array.isArray(init.headers)) {
            const header = init.headers.find(h => h[0].toLowerCase() === name.toLowerCase());
            return header ? header[1] : null;
          }
          return (init.headers as Record<string, string>)[name] || (init.headers as Record<string, string>)[name.toLowerCase()];
        }
        if (input instanceof Request) {
          return input.headers.get(name);
        }
        return null;
      };

      const isRSC = getHeader('RSC') === '1';
      const isPrefetch = getHeader('Next-Router-Prefetch') === '1';
      const isNoStore = init?.cache === 'no-store';

      // Bypass for non-GET methods, Next.js internal requests, or explicit no-store
      if (method !== 'GET' || isRSC || isPrefetch || isNoStore) {
        return originalFetch(input, init);
      }

      // Generate a cache key
      const cacheKey = `${method}:${url}`;

      // Request Coalescing
      if (inFlight.has(cacheKey)) {
        // console.debug(`[Phantom] Coalescing request for ${url}`);
        return inFlight.get(cacheKey)!.then(res => res.clone());
      }

      // console.debug(`[Phantom] Fetching ${url}`);
      const promise = originalFetch(input, init);

      const coalescedPromise = promise.then(res => {
        inFlight.delete(cacheKey);
        return res;
      }).catch(err => {
        inFlight.delete(cacheKey);
        throw err;
      });

      inFlight.set(cacheKey, coalescedPromise);

      return coalescedPromise.then(res => res.clone());
    };
  }, []);

  return <>{children}</>;
}
