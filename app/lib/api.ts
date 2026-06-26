/**
 * Invisible Infrastructure: Request Coalescing & Stale-While-Revalidate Cache
 * Eliminates duplicate network requests and provides instant responses for hot data.
 */

const inFlight = new Map<string, Promise<Response>>();
const responseCache = new Map<string, { res: Response; timestamp: number }>();

const CACHE_TTL_MS = 10000; // 10 seconds for stale-while-revalidate

export async function dedupedFetch(url: string, options?: RequestInit): Promise<Response> {
  const method = options?.method?.toUpperCase() || 'GET';

  // Only deduplicate and cache GET requests
  if (method !== 'GET') {
    return fetch(url, options);
  }

  const cacheKey = `${method}:${url}`;

  // 1. Return in-flight request if one exists (Request Coalescing)
  if (inFlight.has(cacheKey)) {
    console.debug(`🌀 Phantom [Coalescing]: Deduping simultaneous request for ${cacheKey}`);
    return inFlight.get(cacheKey)!.then(res => res.clone());
  }

  // 2. Check cache for Stale-While-Revalidate
  const cached = responseCache.get(cacheKey);
  const isStale = !cached || (Date.now() - cached.timestamp > CACHE_TTL_MS);

  if (cached && !isStale) {
    console.debug(`🌀 Phantom [Cache Hit]: Serving fresh data for ${cacheKey}`);
    return cached.res.clone();
  }

  // 3. Make the actual network request
  const fetchPromise = fetch(url, options)
    .then(res => {
      if (res.ok) {
        // Cache successful responses
        responseCache.set(cacheKey, { res: res.clone(), timestamp: Date.now() });
      }
      return res;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, fetchPromise);

  // If we have stale data, serve it immediately while the fresh fetch happens in background
  if (cached && isStale) {
    console.debug(`🌀 Phantom [Stale-While-Revalidate]: Serving stale data while refreshing ${cacheKey}`);
    // We swallow the unhandled rejection in background so it doesn't crash the app
    fetchPromise.catch(() => {});
    return cached.res.clone();
  }

  // Otherwise wait for the fresh fetch
  return fetchPromise.then(res => res.clone());
}
