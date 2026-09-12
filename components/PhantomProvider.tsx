'use client';

import React from 'react';

// Initialize outside React lifecycle to catch early requests
if (typeof window !== 'undefined' && !('__fetchPatched' in window)) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (window as any).__fetchPatched = true;

  const originalFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    // 1. Bypass check
    // We shouldn't deduplicate if there's an abort signal,
    // or if it's a non-GET request, or if it has Next.js internal RSC headers.

    const reqMethod = (input instanceof Request ? input.method : init?.method) || 'GET';
    const isGet = reqMethod.toUpperCase() === 'GET';
    const hasAbortSignal = !!(init?.signal || (input instanceof Request ? input.signal : null));

    // Check headers
    let isNextInternal = false;
    let headersObj: Headers;
    if (init?.headers) {
      headersObj = new Headers(init.headers as HeadersInit);
    } else if (input instanceof Request) {
      headersObj = input.headers;
    } else {
      headersObj = new Headers();
    }
    if (headersObj) {
      if (headersObj.has('RSC') || headersObj.has('Next-Router-State-Tree')) {
        isNextInternal = true;
      }
    }

    if (!isGet || hasAbortSignal || isNextInternal) {
      return originalFetch(input, init);
    }

    // 2. Generate Cache Key
    const urlString = typeof input === 'string' ? input : (input instanceof URL ? input.toString() : (input as Request).url);

    // Serialize headers for the key
    let headersString = '';
    if (headersObj) {
      const headerKeys = Array.from(headersObj.keys()).sort();
      headersString = headerKeys.map(k => `${k}:${headersObj.get(k)}`).join('|');
    }

    const cacheKey = `${urlString}:::${headersString}`;

    // 3. Deduplicate
    if (inFlight.has(cacheKey)) {
      const promise = inFlight.get(cacheKey)!;
      // Must clone the response for all consumers
      const res = await promise;
      return res.clone();
    }

    // Create a new promise and store it
    const fetchPromise = originalFetch(input, init)
      .finally(() => {
        inFlight.delete(cacheKey);
      });

    inFlight.set(cacheKey, fetchPromise);

    const res = await fetchPromise;
    return res.clone();
  };
}

export default function PhantomProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
