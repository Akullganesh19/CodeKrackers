const MAX_CACHE_SIZE = 50;

interface CacheEntry {
  response: Response;
  timestamp: number;
}

const cache = new Map<string, CacheEntry>();
const inFlight = new Map<string, Promise<Response>>();

export async function phantomFetch(url: string | URL, options?: RequestInit): Promise<Response> {
  const isGet = !options?.method || options.method.toUpperCase() === 'GET';
  const cacheKey = url.toString() + (options?.headers ? JSON.stringify(options.headers) : '');

  // If not a GET request, just pass through to native fetch
  if (!isGet) {
    return fetch(url, options);
  }

  // 1. Stale-While-Revalidate
  const cached = cache.get(cacheKey);

  if (cached) {
    // Update access timestamp for LRU
    cached.timestamp = Date.now();

    // Background revalidation
    revalidate(cacheKey, url, options).catch(() => {});
    return cached.response.clone();
  }

  // 2. Request Coalescing
  return deduplicatedFetch(cacheKey, url, options);
}

async function deduplicatedFetch(cacheKey: string, url: string | URL, options?: RequestInit): Promise<Response> {
  if (inFlight.has(cacheKey)) {
    const promise = inFlight.get(cacheKey)!;
    const res = await promise;
    return res.clone();
  }

  const promise = fetch(url, options)
    .then((res) => {
      if (res.ok) {
        updateCache(cacheKey, res.clone());
      }
      return res;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);

  const res = await promise;
  return res.clone();
}

async function revalidate(cacheKey: string, url: string | URL, options?: RequestInit) {
  if (inFlight.has(cacheKey)) return; // Already fetching/revalidating

  const promise = fetch(url, options)
    .then((res) => {
      if (res.ok) {
        updateCache(cacheKey, res.clone());
      }
      return res;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);
  await promise;
}

function updateCache(key: string, response: Response) {
  if (cache.size >= MAX_CACHE_SIZE && !cache.has(key)) {
    // LRU Eviction
    let oldestKey: string | null = null;
    let oldestTime = Infinity;

    for (const [k, v] of cache.entries()) {
      if (v.timestamp < oldestTime) {
        oldestTime = v.timestamp;
        oldestKey = k;
      }
    }

    if (oldestKey) {
      cache.delete(oldestKey);
    }
  }

  cache.set(key, {
    response,
    timestamp: Date.now()
  });
}
