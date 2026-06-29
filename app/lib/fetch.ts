const inFlight = new Map<string, Promise<Response>>();
const cache = new Map<string, { response: Response; timestamp: number }>();

const CACHE_TTL = 5000; // 5 seconds strictly fresh
const SWR_TTL = 60000; // 60 seconds stale-while-revalidate
const MAX_CACHE_SIZE = 100; // Prevent unbound memory growth

function enforceCacheSize() {
  if (cache.size > MAX_CACHE_SIZE) {
    // Map iterates in insertion order, so the first key is the oldest
    const oldestKey = cache.keys().next().value;
    if (oldestKey) cache.delete(oldestKey);
  }
}

/**
 * Invisible Infrastructure:
 * Deduped and cached fetch to prevent multiple identical requests from firing
 * simultaneously or wasting bandwidth on duplicate requests.
 * Implements Request Coalescing and Stale-While-Revalidate caching.
 */
export async function phantomFetch(url: string, options?: RequestInit): Promise<Response> {
  const method = options?.method || 'GET';

  // Only coalesce and cache GET requests. Mutations bypass this.
  if (method.toUpperCase() !== 'GET') {
    return fetch(url, options);
  }

  const cacheKey = JSON.stringify({
    url,
    headers: options?.headers || {},
  });

  const now = Date.now();
  const cached = cache.get(cacheKey);

  // 1. Fresh Cache Hit -> Return instantly
  if (cached && now - cached.timestamp < CACHE_TTL) {
    return cached.response.clone();
  }

  // 2. Request Coalescing -> Already fetching? Wait for it or return SWR
  if (inFlight.has(cacheKey)) {
    if (cached && now - cached.timestamp < SWR_TTL) {
      return cached.response.clone(); // Return stale while in-flight happens
    }
    return inFlight.get(cacheKey)!.then(res => res.clone());
  }

  // 3. Network Fetch
  const promise = fetch(url, options)
    .then(res => {
      if (res.ok) {
        cache.set(cacheKey, { response: res.clone(), timestamp: Date.now() });
        enforceCacheSize();
      } else {
        // According to memory guidelines, delete cache if response fails to prevent serving bad state
        cache.delete(cacheKey);
      }
      return res;
    })
    .catch(err => {
        cache.delete(cacheKey);
        throw err;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);

  // 4. Stale-While-Revalidate
  // Return stale data immediately while the fetch happens in the background
  if (cached && now - cached.timestamp < SWR_TTL) {
    // Attach a dummy catch to prevent UnhandledPromiseRejection since the caller
    // receives the cached response and won't await this promise chain.
    promise.catch(() => {});
    return cached.response.clone();
  }

  // 5. No cache or too stale -> Wait for network
  return promise.then(res => res.clone());
}
