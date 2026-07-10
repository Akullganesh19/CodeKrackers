// phantomFetch.ts - Invisible infrastructure for request coalescing and caching
// Features: Request deduping (coalescing), TTL-based in-memory caching, graceful degradation

interface CacheEntry {
  promise: Promise<Response>;
  timestamp: number;
}

// Module-level global to survive component unmounts and enable cross-component coalescing
const cache: Record<string, CacheEntry> = {};
const TTL_MS = 5000; // 5 seconds TTL for hot path data

function generateCacheKey(input: RequestInfo | URL, init?: RequestInit): string {
  const url = typeof input === 'string' ? input : 'url' in input ? input.url : input.toString();

  // Only cache GET requests (or requests without a method, which default to GET)
  const method = init?.method?.toUpperCase() || 'GET';
  if (method !== 'GET') return ''; // Don't cache non-GET requests

  let headersString = '';
  if (init?.headers) {
    if (init.headers instanceof Headers) {
      headersString = JSON.stringify(Object.fromEntries(init.headers.entries()));
    } else {
      headersString = JSON.stringify(init.headers);
    }
  }

  // Include token from localStorage if present to prevent cross-user cache collisions
  let token = '';
  if (typeof window !== 'undefined') {
    token = localStorage.getItem('vsdp_token') || '';
  }

  return `${method}:${url}:${headersString}:${token}`;
}

export const phantomFetch = async (
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> => {
  const key = generateCacheKey(input, init);

  // If uncacheable, just pass through
  if (!key) {
    return fetch(input, init);
  }

  const now = Date.now();
  const cached = cache[key];

  // 1. Return fresh cached promise/response if within TTL
  if (cached && now - cached.timestamp < TTL_MS) {
    try {
      const res = await cached.promise;
      // Always clone response so multiple consumers can .json() it
      return res.clone();
    } catch (e) {
      // If the cached promise failed, we fall through and retry
      delete cache[key];
    }
  }

  // 2. Otherwise, fire off a new request and cache the promise (Coalescing)
  // This means 10 simultaneous callers will await the EXACT same fetch promise
  const promise = fetch(input, init)
    .then((res) => {
      // Don't cache non-2xx responses (like 400, 500), but we MUST return them to caller
      // so caller can read res.status or res.json().
      if (!res.ok) {
        delete cache[key];
      }
      return res;
    })
    .catch((err) => {
      // On network failure (which throws natively in fetch), remove from cache so next try makes a real network request
      delete cache[key];
      // We rethrow the error to the caller instead of returning a mock 500 response,
      // ensuring we match standard fetch semantics for true network failures.
      throw err;
    });

  cache[key] = { promise, timestamp: now };

  const res = await promise;
  return res.clone();
};
