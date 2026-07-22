export interface CacheEntry {
  response: Response;
  timestamp: number;
  revalidating: boolean;
}

const CACHE_TTL_MS = 60 * 1000; // 60 seconds
const MAX_CACHE_ENTRIES = 100;
const MAX_RETRIES = 3;
const BASE_BACKOFF_MS = 500;

const cache = new Map<string, CacheEntry>();
const inFlight = new Map<string, Promise<Response>>();

function evictOldestIfNeeded() {
  if (cache.size >= MAX_CACHE_ENTRIES) {
    let oldestKey: string | null = null;
    let oldestTime = Infinity;
    for (const [key, entry] of cache.entries()) {
      if (entry.timestamp < oldestTime) {
        oldestTime = entry.timestamp;
        oldestKey = key;
      }
    }
    if (oldestKey) {
      cache.delete(oldestKey);
    }
  }
}

async function performFetchWithRetries(
  req: Request,
  retries = MAX_RETRIES,
  backoff = BASE_BACKOFF_MS
): Promise<Response> {
  try {
    const res = await fetch(req.clone());

    // Do not retry 4xx errors, but maybe 5xx
    if (!res.ok && res.status >= 500 && retries > 0 && isIdempotent(req.method)) {
      throw new Error(`Server error: ${res.status}`);
    }
    return res;
  } catch (error) {
    if (retries > 0 && isIdempotent(req.method)) {
      await new Promise((resolve) => setTimeout(resolve, backoff));
      return performFetchWithRetries(req, retries - 1, backoff * 2);
    }
    throw error;
  }
}

function isIdempotent(method: string) {
  const m = method.toUpperCase();
  return m === 'GET' || m === 'PUT' || m === 'DELETE' || m === 'HEAD' || m === 'OPTIONS';
}

export async function phantomFetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  const req = new Request(input, init);
  const url = req.url;
  const method = req.method.toUpperCase();

  // If mutation, invalidate cache for this URL
  if (method !== 'GET') {
    cache.delete(url);
    return performFetchWithRetries(req);
  }

  const now = Date.now();
  const cached = cache.get(url);

  // Cache hit
  if (cached) {
    const isStale = now - cached.timestamp > CACHE_TTL_MS;

    if (isStale && !cached.revalidating) {
      cached.revalidating = true;

      const backgroundPromise = performFetchWithRetries(req.clone())
        .then((res) => {
          if (res.ok) {
            evictOldestIfNeeded();
            cache.set(url, { response: res.clone(), timestamp: Date.now(), revalidating: false });
          }
        })
        .catch(() => {
          // On failure, we don't update cache but we might clear it or leave stale
        })
        .finally(() => {
          const entry = cache.get(url);
          if (entry) {
            entry.revalidating = false;
          }
        });

        // If we don't have inFlight for this, maybe set it, but SWR is background
    }

    // Always clone the cached response so callers can read the body
    return cached.response.clone();
  }

  // Coalesce in-flight requests
  if (inFlight.has(url)) {
    const res = await inFlight.get(url)!;
    return res.clone();
  }

  // Not in cache, not in flight
  const fetchPromise = performFetchWithRetries(req.clone())
    .then((res) => {
      if (res.ok) {
        evictOldestIfNeeded();
        cache.set(url, { response: res.clone(), timestamp: Date.now(), revalidating: false });
      }
      return res;
    })
    .finally(() => {
      inFlight.delete(url);
    });

  inFlight.set(url, fetchPromise);

  const finalRes = await fetchPromise;
  return finalRes.clone();
}
