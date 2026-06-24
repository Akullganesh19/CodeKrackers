// Request coalescing & basic SWR cache
const inFlight = new Map<string, Promise<Response>>();
const cache = new Map<string, { data: any, timestamp: number }>();
const CACHE_TTL = 30000; // 30 seconds

export async function dedupedFetch(url: string, options?: RequestInit): Promise<Response> {
  // Only dedupe and cache GET requests
  if (options && options.method && options.method.toUpperCase() !== 'GET') {
    return fetch(url, options);
  }
  if (!options?.method && options) {
    // Treat as GET if no method is specified but options exist
  }

  const cacheKey = url + JSON.stringify(options?.headers || {});

  // Return cached data if valid
  if (cache.has(cacheKey)) {
    const { data, timestamp } = cache.get(cacheKey)!;
    if (Date.now() - timestamp < CACHE_TTL) {
      // Background revalidation (stale-while-revalidate)
      if (Date.now() - timestamp > CACHE_TTL / 2) {
        doFetch(url, options, cacheKey).catch(console.error);
      }
      return new Response(new Blob([JSON.stringify(data)], { type: 'application/json' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  if (inFlight.has(cacheKey)) {
    return (await inFlight.get(cacheKey)!).clone();
  }

  const promise = doFetch(url, options, cacheKey);
  inFlight.set(cacheKey, promise);

  try {
    const res = await promise;
    return res.clone();
  } finally {
    inFlight.delete(cacheKey);
  }
}

async function doFetch(url: string, options: RequestInit | undefined, cacheKey: string): Promise<Response> {
  const res = await fetch(url, options);
  if (res.ok) {
    const clone = res.clone();
    try {
      const data = await clone.json();
      cache.set(cacheKey, { data, timestamp: Date.now() });
    } catch (e) {
      // Not JSON, skip caching
    }
  }
  return res;
}
