'use client';

import React from 'react';

// Module scope to ensure it runs synchronously before children mount
let isInitialized = false;

if (typeof window !== 'undefined' && !isInitialized) {
  isInitialized = true;

  const originalFetch = window.fetch;
  const inFlightRequests = new Map<string, Promise<Response>>();
  const cache = new Map<string, { data: ArrayBuffer; timestamp: number; headers: Headers }>();
  const CACHE_TTL = 5000; // 5 seconds fresh time

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    let url = '';
    let method = 'GET';

    if (typeof input === 'string') {
      url = input;
    } else if (input instanceof URL) {
      url = input.toString();
    } else if (input instanceof Request) {
      url = input.url;
      method = input.method || 'GET';
    }

    if (init && init.method) {
      method = init.method;
    }

    method = method.toUpperCase();

    // Only coalesce and cache GET requests
    if (method !== 'GET') {
      return originalFetch(input, init);
    }

    const cacheKey = url;

    // 1. Request Coalescing
    if (inFlightRequests.has(cacheKey)) {
      console.debug('🌀 [Phantom] Coalesced request:', cacheKey);
      const promise = inFlightRequests.get(cacheKey)!;
      const res = await promise;
      return res.clone();
    }

    // 2. Stale-while-revalidate Cache
    const cached = cache.get(cacheKey);
    const now = Date.now();

    if (cached) {
      if (now - cached.timestamp < CACHE_TTL) {
        // Fresh enough, serve immediately
        console.debug('🌀 [Phantom] Cache HIT (Fresh):', cacheKey);

        // Clone headers to allow modification
        const resHeaders = new Headers(cached.headers);
        resHeaders.set('X-Phantom-Cache', 'hit');

        return new Response(cached.data, {
          status: 200,
          statusText: 'OK',
          headers: resHeaders
        });
      }

      // Stale - trigger background refresh
      console.debug('🌀 [Phantom] Cache STALE (Background fetching):', cacheKey);
      const backgroundPromise = originalFetch(input, init).then(res => {
        if (res.ok) {
          const cacheClone = res.clone();
          cacheClone.arrayBuffer().then(buffer => {
            cache.set(cacheKey, {
              data: buffer,
              timestamp: Date.now(),
              headers: res.headers
            });
          }).catch(() => {}); // Silent catch for background cache write
        }
        return res;
      }).finally(() => {
        inFlightRequests.delete(cacheKey);
      });
      // Attach catch purely to prevent unhandled rejection since backgroundPromise is not awaited
      backgroundPromise.catch(() => {});

      inFlightRequests.set(cacheKey, backgroundPromise);

      const staleHeaders = new Headers(cached.headers);
      staleHeaders.set('X-Phantom-Cache', 'stale');

      return new Response(cached.data, {
        status: 200,
        statusText: 'OK',
        headers: staleHeaders
      });
    }

    // 3. Normal fetch (Miss)
    console.debug('🌀 [Phantom] Cache MISS (Fetching):', cacheKey);
    const fetchPromise = originalFetch(input, init).then(res => {
      if (res.ok) {
        const cacheClone = res.clone();
        cacheClone.arrayBuffer().then(buffer => {
          cache.set(cacheKey, {
            data: buffer,
            timestamp: Date.now(),
            headers: res.headers
          });
        }).catch(() => {});
      }
      return res;
    }).finally(() => {
      inFlightRequests.delete(cacheKey);
    });

    inFlightRequests.set(cacheKey, fetchPromise);
    const resolvedRes = await fetchPromise;

    const returnRes = resolvedRes.clone();
    const returnHeaders = new Headers(returnRes.headers);
    returnHeaders.set('X-Phantom-Cache', 'miss');

    return new Response(returnRes.body, {
      status: returnRes.status,
      statusText: returnRes.statusText,
      headers: returnHeaders
    });
  };
}

export function PhantomInfrastructure({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
