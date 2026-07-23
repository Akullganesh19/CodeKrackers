'use client'

import { useEffect } from 'react'

interface CacheEntry {
  response: Response;
  timestamp: number;
  revalidating: boolean;
}

const CACHE_TTL_MS = 10000; // 10 seconds
const MAX_CACHE_SIZE = 100;

const IN_FLIGHT: Record<string, Promise<Response>> = {};
const CACHE: Record<string, CacheEntry> = {};

const enforceEvictionPolicy = () => {
  const keys = Object.keys(CACHE);
  if (keys.length > MAX_CACHE_SIZE) {
    let oldestKey = keys[0];
    let oldestTime = CACHE[oldestKey].timestamp;
    for (let i = 1; i < keys.length; i++) {
      if (CACHE[keys[i]].timestamp < oldestTime) {
        oldestTime = CACHE[keys[i]].timestamp;
        oldestKey = keys[i];
      }
    }
    delete CACHE[oldestKey];
  }
};

export function PhantomProvider() {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    if ('__phantomWrapped' in window.fetch) return;

    const nativeFetch = window.fetch;

    const phantomFetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      // Determine method safely
      let method = init?.method?.toUpperCase();
      if (!method && input instanceof Request) {
        method = input.method.toUpperCase();
      }
      method = method || 'GET';

      if (method !== 'GET' || init?.cache === 'no-store') {
        return nativeFetch(input, init);
      }

      let urlKey: string;
      try {
        urlKey = new Request(input, init).url;
      } catch {
        return nativeFetch(input, init);
      }

      const now = Date.now();

      if (urlKey in CACHE) {
        const cached = CACHE[urlKey];
        const isStale = now - cached.timestamp > CACHE_TTL_MS;

        if (isStale && !cached.revalidating) {
          cached.revalidating = true;

          nativeFetch(input, init)
            .then(res => {
              if (res.ok) {
                CACHE[urlKey] = {
                  response: res.clone(),
                  timestamp: Date.now(),
                  revalidating: false
                };
                enforceEvictionPolicy();
              } else {
                delete CACHE[urlKey];
              }
              return null;
            })
            .catch(() => {
              return null;
            })
            .finally(() => {
              if (urlKey in CACHE) {
                CACHE[urlKey].revalidating = false;
              }
            });
        }

        return cached.response.clone();
      }

      if (urlKey in IN_FLIGHT) {
        return IN_FLIGHT[urlKey].then(res => res.clone());
      }

      const promise = nativeFetch(input, init)
        .then(res => {
          if (res.ok) {
            CACHE[urlKey] = {
              response: res.clone(),
              timestamp: Date.now(),
              revalidating: false
            };
            enforceEvictionPolicy();
          }
          return res;
        })
        .finally(() => {
          delete IN_FLIGHT[urlKey];
        });

      IN_FLIGHT[urlKey] = promise;

      return promise.then(res => res.clone());
    };

    (phantomFetch as any).__phantomWrapped = true;
    window.fetch = phantomFetch as typeof window.fetch;

    return () => {
      window.fetch = nativeFetch;
    };
  }, []);

  return null;
}
