'use client'

import { useEffect, ReactNode, useRef } from 'react';

// Initialize outside of useEffect so it runs immediately during the first render cycle
// before children can run their effects.
if (typeof window !== 'undefined') {
  const win = window as any;
  if (!win.__phantomInitialized) {
    win.__phantomInitialized = true;

    const nativeFetch = window.fetch;
    const inFlight = new Map<string, Promise<Response>>();

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const urlStr = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;
      const method = (init?.method || (input instanceof Request ? input.method : 'GET')).toUpperCase();

      const isGet = method === 'GET';
      const noStore = init?.cache === 'no-store' || (input instanceof Request && input.cache === 'no-store');

      let isRsc = false;
      if (init?.headers) {
        const headers = new Headers(init.headers);
        isRsc = headers.has('RSC') || headers.has('Next-Router-Prefetch');
      } else if (input instanceof Request) {
        isRsc = input.headers.has('RSC') || input.headers.has('Next-Router-Prefetch');
      }

      if (!isGet || noStore || isRsc) {
        return nativeFetch(input, init);
      }

      const cacheKey = urlStr;

      let promise = inFlight.get(cacheKey);
      if (!promise) {
        promise = nativeFetch(input, init).finally(() => {
          inFlight.delete(cacheKey);
        });
        inFlight.set(cacheKey, promise);
      }

      const result = await promise;
      return result.clone();
    };
    console.log("🌀 Phantom infrastructure initialized: Global Request Coalescing active.");
  }
}

export function PhantomProvider({ children }: { children: ReactNode }) {
  // Empty effect just to keep it as a valid Client Component hook usage if needed
  useEffect(() => {}, []);
  return <>{children}</>;
}
