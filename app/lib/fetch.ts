const MAX_CACHE_SIZE = 100;

interface CacheEntry {
  response: Response;
  timestamp: number;
}

const cache = new Map<string, CacheEntry>();
const inFlight = new Map<string, Promise<Response>>();

export async function phantomFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;
  const method = init?.method?.toUpperCase() || 'GET';

  if (method !== 'GET') {
    return fetch(input, init);
  }

  // Use URL and Authorization header as cache key
  const authHeader = (init?.headers as Record<string, string>)?.['Authorization'] || '';
  const cacheKey = `${url}|${authHeader}`;

  const cached = cache.get(cacheKey);

  let fetchPromise = inFlight.get(cacheKey);
  if (!fetchPromise) {
    fetchPromise = fetch(input, init)
      .then(res => {
        if (!res.ok) {
          cache.delete(cacheKey);
          return res;
        }

        const cloned = res.clone();

        // LRU eviction
        if (cache.size >= MAX_CACHE_SIZE && !cache.has(cacheKey)) {
          const oldestKey = cache.keys().next().value;
          if (oldestKey) cache.delete(oldestKey);
        }

        cache.set(cacheKey, {
          response: cloned,
          timestamp: Date.now()
        });

        return res;
      })
      .catch(err => {
        // Fallback response for graceful degradation
        return new Response(JSON.stringify({ error: 'Network error', details: String(err) }), {
          status: 503,
          statusText: 'Service Unavailable',
          headers: { 'Content-Type': 'application/json' }
        });
      })
      .finally(() => {
        inFlight.delete(cacheKey);
      });

    // Silent catch to prevent UnhandledPromiseRejection on background refresh
    fetchPromise.catch(() => {});

    inFlight.set(cacheKey, fetchPromise);
  }

  if (cached) {
    // SWR: return cached immediately, background fetch updates cache
    return cached.response.clone();
  }

  return fetchPromise.then(res => res.clone());
}
