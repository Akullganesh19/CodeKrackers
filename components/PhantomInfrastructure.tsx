'use client';

import { useEffect } from 'react';

// SWR Cache & Coalescing maps
const inFlight = new Map<string, Promise<Response>>();

interface CacheEntry {
  response: Response;
  timestamp: number;
  revalidating: boolean;
}
const cache = new Map<string, CacheEntry>();

const CACHE_TTL = 1000 * 60 * 5; // 5 minutes fresh
const MAX_CACHE_ITEMS = 100;

export default function PhantomInfrastructure() {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Save original fetch
    const originalFetch = window.fetch;

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      // 1. Bypass check
      const method = (input instanceof Request ? input.method : init?.method || 'GET').toUpperCase();
      if (
        method !== 'GET' ||
        init?.cache === 'no-store' ||
        init?.cache === 'no-cache'
      ) {
        return originalFetch(input, init);
      }

      // 2. Normalize URL safely without consuming Request body
      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;

      // Ensure we don't cache internal Next.js requests if any, though normally this is fine
      // But we just use a generic cache key
      const cacheKey = url;

      // 3. Check Cache
      const cached = cache.get(cacheKey);
      const now = Date.now();

      if (cached) {
        const isStale = now - cached.timestamp > CACHE_TTL;

        if (isStale && !cached.revalidating) {
          // Stale-While-Revalidate
          cached.revalidating = true;

          // Background fetch
          const bgPromise = originalFetch(input, init)
            .then(res => {
              if (res.ok) {
                // Enforce eviction
                if (cache.size >= MAX_CACHE_ITEMS) {
                  const firstKey = cache.keys().next().value;
                  if (firstKey) cache.delete(firstKey);
                }
                cache.set(cacheKey, {
                  response: res.clone(),
                  timestamp: Date.now(),
                  revalidating: false
                });
              }
              return res;
            })
            .catch(err => {
              // Swallow background errors so they don't crash the app
              console.warn('Phantom SWR background fetch failed:', err);
              return null;
            })
            .finally(() => {
              const current = cache.get(cacheKey);
              if (current) current.revalidating = false;
            });

            // Do not await background promise, just let it run
        }

        return cached.response.clone();
      }

      // 4. Request Coalescing (Deduplication)
      if (inFlight.has(cacheKey)) {
        const promise = inFlight.get(cacheKey)!;
        return promise.then(res => res.clone());
      }

      // 5. Native Fetch with Caching
      const fetchPromise = originalFetch(input, init)
        .then(res => {
          if (res.ok) {
            // Enforce eviction
            if (cache.size >= MAX_CACHE_ITEMS) {
              const firstKey = cache.keys().next().value;
              if (firstKey) cache.delete(firstKey);
            }
            cache.set(cacheKey, {
              response: res.clone(),
              timestamp: Date.now(),
              revalidating: false
            });
          }
          return res;
        })
        .finally(() => {
          inFlight.delete(cacheKey);
        });

      inFlight.set(cacheKey, fetchPromise);

      // Await and return clone so the original is safe in cache/inFlight
      return (await fetchPromise).clone();
    };

    // Cleanup: restore original fetch on unmount (rare, but good practice)
    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  return null; // Invisible infrastructure
}
