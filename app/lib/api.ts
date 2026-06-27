const inFlight = new Map<string, Promise<Response>>();
const cache = new Map<string, { data: Response; timestamp: number }>();
const CACHE_TTL = 5000; // 5 seconds for stale-while-revalidate

export async function dedupedFetch(url: string | URL, options?: RequestInit): Promise<Response> {
  // Include Authorization header in cache key if present to prevent caching across user sessions
  let authHeader = '';
  if (options?.headers) {
    const headers = new Headers(options.headers);
    authHeader = headers.get('Authorization') || '';
  }
  const baseUrl = typeof url === 'string' ? url : url.toString();
  const cacheKey = `${baseUrl}|${authHeader}`;

  // Only deduplicate GET requests
  if (options?.method && options.method.toUpperCase() !== 'GET') {
    return fetch(url, options);
  }

  // 1. Check if we have a response in cache
  const cached = cache.get(cacheKey);
  if (cached) {
    const isStale = Date.now() - cached.timestamp >= CACHE_TTL;
    if (isStale) {
      // Return a clone immediately, but kick off a background refresh (stale-while-revalidate)
      refreshCache(url, options, cacheKey);
    }
    // Return cached response (fresh or stale while revalidating)
    return cached.data.clone();
  }

  // 2. Check if there's already an in-flight request for this URL
  if (inFlight.has(cacheKey)) {
    return inFlight.get(cacheKey)!.then(res => res.clone());
  }

  // 3. Make the actual request and store the promise
  const promise = fetch(url, options)
    .then(res => {
      if (res.ok) {
        // Cache the successful response
        cache.set(cacheKey, { data: res.clone(), timestamp: Date.now() });
      }
      return res;
    })
    .catch(err => {
      // If the request fails, remove it from the cache so we can retry later
      inFlight.delete(cacheKey);
      throw err;
    })
    .finally(() => {
      // Always remove from in-flight when done (success or failure)
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);

  return promise.then(res => res.clone());
}

function refreshCache(url: string | URL, options: RequestInit | undefined, cacheKey: string) {
  // Don't refresh if there's already an active request
  if (inFlight.has(cacheKey)) return;

  const promise = fetch(url, options)
    .then(res => {
      if (res.ok) {
        cache.set(cacheKey, { data: res.clone(), timestamp: Date.now() });
      }
      return res;
    })
    .catch(err => {
      // Silently catch background refresh errors to prevent unhandled promise rejections
      console.warn(`Background refresh failed for ${url}:`, err);
      // Return a mocked Response fallback object to degrade gracefully
      // and prevent unhandled promise rejections when awaited elsewhere.
      return new Response(null, { status: 500, statusText: "Background Refresh Failed" });
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);
}
