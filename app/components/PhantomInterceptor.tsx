'use client';

import { useEffect } from 'react';

// Prevent re-initialization in React strict mode or HMR
if (typeof window !== 'undefined' && !(window as any).__phantom_initialized) {
  (window as any).__phantom_initialized = true;
  console.log("🌀 Phantom infrastructure: Request coalescing initialized.");

  const nativeFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();

  window.fetch = async function (input: RequestInfo | URL, init?: RequestInit) {
    if (init?.cache === 'no-store') {
      return nativeFetch(input, init);
    }

    const url = typeof input === 'string'
      ? input
      : input instanceof URL
        ? input.toString()
        : input.url;

    const method = (input instanceof Request ? input.method : init?.method || 'GET').toUpperCase();

    if (method !== 'GET') {
      return nativeFetch(input, init);
    }

    const cacheKey = url;

    if (inFlight.has(cacheKey)) {
      console.log(`🌀 Phantom coalesced duplicate fetch for: ${cacheKey}`);
      try {
        const response = await inFlight.get(cacheKey)!;
        return response.clone();
      } catch (err) {
        // Fallback if the inflight promise rejects for some reason
        return nativeFetch(input, init);
      }
    }

    const promise = nativeFetch(input, init);
    inFlight.set(cacheKey, promise);

    try {
      const response = await promise;
      return response.clone();
    } finally {
      inFlight.delete(cacheKey);
    }
  };
}

export default function PhantomInterceptor() {
  // Purely side-effect component, renders nothing
  return null;
}
