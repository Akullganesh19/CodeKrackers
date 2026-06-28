/**
 * Phantom's Request Coalescing and Caching Layer.
 *
 * This prevents the frontend from firing multiple identical requests
 * simultaneously and caches GET requests with a short TTL (Stale-while-revalidate).
 * It ensures background fetching is silent and UI updates seamlessly.
 */

interface CacheEntry {
  promise: Promise<Response>;
  timestamp: number;
}

const CACHE_TTL_MS = 30000; // 30 seconds

// In-flight requests are deduplicated.
const inFlightRequests = new Map<string, Promise<Response>>();

// Successful responses are cached.
const responseCache = new Map<string, CacheEntry>();

export async function dedupedFetch(
  url: string,
  options?: RequestInit & { forceUpdate?: boolean }
): Promise<Response> {
  const method = options?.method?.toUpperCase() || 'GET';

  // We only cache and deduplicate GET requests
  if (method !== 'GET') {
    return fetch(url, options);
  }

  // Get auth from headers or fallback to local storage
  const headers = options?.headers as Record<string, string>;
  const authHeader = headers?.['Authorization'] || headers?.['authorization'];
  const token = typeof window !== 'undefined' ? localStorage.getItem('vsdp_token') : '';

  // Include token in cache key so different users don't share cached data
  const cacheKey = `${url}|${authHeader || token}`;

  // Check valid cache unless forced
  if (!options?.forceUpdate && responseCache.has(cacheKey)) {
    const entry = responseCache.get(cacheKey)!;
    if (Date.now() - entry.timestamp < CACHE_TTL_MS) {
      // Return a cloned response so it can be read multiple times
      const cachedPromise = entry.promise.then(res => res.clone());

      // STALE-WHILE-REVALIDATE: If it's getting old (> 10s), kick off a background refresh
      if (Date.now() - entry.timestamp > 10000 && !inFlightRequests.has(cacheKey)) {
        refreshCacheInBackground(url, options, cacheKey);
      }
      return cachedPromise;
    } else {
      // Expired
      responseCache.delete(cacheKey);
    }
  }

  // Request Coalescing: If already in flight, wait for it
  if (inFlightRequests.has(cacheKey)) {
    return inFlightRequests.get(cacheKey)!.then(res => res.clone());
  }

  // Execute actual network request
  const fetchPromise = fetch(url, options)
    .then(response => {
      // Only cache successful responses
      if (response.ok) {
        responseCache.set(cacheKey, {
          promise: Promise.resolve(response.clone()),
          timestamp: Date.now()
        });
      }
      return response;
    })
    .finally(() => {
      inFlightRequests.delete(cacheKey);
    });

  inFlightRequests.set(cacheKey, fetchPromise);
  return fetchPromise.then(res => res.clone());
}

async function refreshCacheInBackground(url: string, options: RequestInit | undefined, cacheKey: string) {
  const fetchPromise = fetch(url, options)
    .then(response => {
      if (response.ok) {
        responseCache.set(cacheKey, {
          promise: Promise.resolve(response.clone()),
          timestamp: Date.now()
        });
      }
      return response;
    })
    .finally(() => {
      inFlightRequests.delete(cacheKey);
    });
  inFlightRequests.set(cacheKey, fetchPromise);
}
