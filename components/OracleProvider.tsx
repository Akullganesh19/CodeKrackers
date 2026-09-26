'use client'

import React, { ReactNode } from 'react'

let isInitialized = false;

type CacheEntry = {
  promise: Promise<Response>;
  timestamp: number;
};

// We bound the cache
const MAX_CACHE_AGE_MS = 1000 * 60; // 1 min

const predictionCache: Record<string, CacheEntry> = {};
const debounceTimers: Record<string, NodeJS.Timeout> = {};

// Clean up stale cache periodically
if (typeof window !== 'undefined') {
  setInterval(() => {
    const now = Date.now();
    for (const key of Object.keys(predictionCache)) {
      if (now - predictionCache[key].timestamp > MAX_CACHE_AGE_MS) {
        delete predictionCache[key];
      }
    }
  }, 10000);
}

export function predictFetch(input: RequestInfo | URL, init?: RequestInit) {
  if (typeof window === 'undefined') return;

  let urlStr = '';
  if (input instanceof Request) {
    urlStr = input.url;
  } else {
    urlStr = input.toString();
  }

  const method = init?.method || (input instanceof Request ? input.method : 'GET');
  let bodyStr = '';
  if (init && init.body) {
    bodyStr = typeof init.body === 'string' ? init.body : JSON.stringify(init.body);
  }

  // Include method in cache key to avoid GET/POST collisions
  const cacheKey = `${method}|${urlStr}|${bodyStr}`;
  const debounceId = urlStr;

  if (debounceTimers[debounceId]) {
    clearTimeout(debounceTimers[debounceId]);
  }

  debounceTimers[debounceId] = setTimeout(() => {
    if (!(cacheKey in predictionCache)) {
      const fetchFn = (window as unknown as Record<string, unknown>)._originalFetch as typeof fetch || window.fetch;

      const p = fetchFn(input, init).then(res => {
        // If it's an HTTP error (4xx, 5xx), don't cache it so we don't poison the real request
        if (!res.ok) {
          delete predictionCache[cacheKey];
        }
        return res;
      });

      predictionCache[cacheKey] = {
        promise: p,
        timestamp: Date.now()
      };

      p.catch(() => {
        // Network errors also clear cache
        if (predictionCache[cacheKey]?.promise === p) {
          delete predictionCache[cacheKey];
        }
      });
    }
  }, 400);
}

if (typeof window !== 'undefined' && !isInitialized) {
  isInitialized = true;

  const originalFetch = window.fetch;
  (window as unknown as Record<string, unknown>)._originalFetch = originalFetch;

  window.fetch = async function (input: RequestInfo | URL, init?: RequestInit) {
    let urlStr = '';
    if (input instanceof Request) {
      urlStr = input.url;
    } else {
      urlStr = input.toString();
    }
    const method = init?.method || (input instanceof Request ? input.method : 'GET');
    let bodyStr = '';
    if (init && init.body) {
      bodyStr = typeof init.body === 'string' ? init.body : JSON.stringify(init.body);
    }

    const cacheKey = `${method}|${urlStr}|${bodyStr}`;

    if (cacheKey in predictionCache) {
      const cachedEntry = predictionCache[cacheKey];
      const promise = cachedEntry.promise;
      delete predictionCache[cacheKey];
      return promise;
    }

    return originalFetch(input, init);
  };
}

export function OracleProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
