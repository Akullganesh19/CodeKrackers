export interface PhantomFetchOptions extends RequestInit {
  /** Time to live in milliseconds for cache. Default 5000 (5s) */
  ttl?: number;
  /** Whether to use stale-while-revalidate pattern. Default true */
  swr?: boolean;
  /** Max retries with exponential backoff for idempotent requests. Default 3 */
  retries?: number;
}

interface CacheEntry {
  response: Response;
  timestamp: number;
}

// In-flight request coalescing map
const inFlight = new Map<string, Promise<Response>>();

// Transparent TTL Cache
const cache = new Map<string, CacheEntry>();
const MAX_CACHE_SIZE = 100;

function enforceCacheSize() {
  if (cache.size > MAX_CACHE_SIZE) {
    const oldestKey = cache.keys().next().value;
    if (oldestKey) cache.delete(oldestKey);
  }
}

/**
 * Generates a cache key containing the URL and Authorization header (if any)
 * to prevent cross-session data leaks.
 */
function generateCacheKey(req: Request): string {
  const urlStr = req.url;
  const authHeader = req.headers.get('Authorization') || '';
  return `${urlStr}|${authHeader}`;
}

async function fetchWithBackoff(
  input: RequestInfo | URL,
  init: RequestInit = {},
  retries: number
): Promise<Response> {
  let attempt = 0;
  while (attempt <= retries) {
    try {
      const response = await fetch(input, init);
      // We don't retry on 4xx errors, only 5xx or network errors
      if (response.status >= 500 && attempt < retries) {
        attempt++;
        await new Promise(res => setTimeout(res, Math.pow(2, attempt) * 500));
        continue;
      }
      return response;
    } catch (err) {
      if (attempt < retries) {
        attempt++;
        await new Promise(res => setTimeout(res, Math.pow(2, attempt) * 500));
        continue;
      }
      throw err;
    }
  }
  throw new Error("Unreachable");
}

export async function phantomFetch(
  input: RequestInfo | URL,
  init?: PhantomFetchOptions
): Promise<Response> {
  // Normalize input to a Request object to correctly extract method and headers
  const req = new Request(input, init);
  const method = req.method.toUpperCase();
  const isIdempotent = ['GET', 'HEAD', 'OPTIONS'].includes(method);

  // Only cache idempotent requests
  if (!isIdempotent) {
    return fetch(req);
  }

  const cacheKey = generateCacheKey(req);
  const ttl = init?.ttl !== undefined ? init.ttl : 5000;
  const swr = init?.swr !== undefined ? init.swr : true;
  const retries = init?.retries !== undefined ? init.retries : 3;
  const now = Date.now();

  const cached = cache.get(cacheKey);

  // Check if we have a valid cache hit
  if (cached) {
    const age = now - cached.timestamp;

    if (age < ttl) {
      // Fresh cache hit - return clone to avoid "body already read"
      console.debug(`[phantomFetch] Cache hit (fresh) for ${req.url}`);
      return cached.response.clone();
    } else if (swr) {
      // Stale cache hit with SWR
      // Fire off revalidation in the background without awaiting it
      console.debug(`[phantomFetch] Cache hit (stale) for ${req.url}. Revalidating in background...`);
      revalidate(req, undefined, cacheKey, retries).catch(err => {
        console.error('SWR revalidation failed for', req.url, err);
      });
      return cached.response.clone();
    }
  }

  // Request Coalescing: return existing in-flight promise if available
  if (inFlight.has(cacheKey)) {
    console.debug(`[phantomFetch] Coalescing request for ${req.url}`);
    const response = await inFlight.get(cacheKey)!;
    // Clone to prevent body consumed errors for multiple coalesced awaiters
    return response.clone();
  }

  console.debug(`[phantomFetch] Fetching fresh data for ${req.url}`);
  // Actual fetch request wrapped in our coalescing map
  const requestPromise = (async () => {
    try {
      const response = await fetchWithBackoff(req, undefined, retries);
      // Only cache successful (2xx) responses
      if (response.ok) {
        cache.set(cacheKey, {
          response: response.clone(),
          timestamp: Date.now()
        });
        enforceCacheSize();
      }
      return response;
    } finally {
      inFlight.delete(cacheKey);
    }
  })();

  inFlight.set(cacheKey, requestPromise);
  const response = await requestPromise;
  return response.clone();
}

async function revalidate(
  input: RequestInfo | URL,
  init: RequestInit | undefined,
  cacheKey: string,
  retries: number
) {
  if (inFlight.has(cacheKey)) {
    return inFlight.get(cacheKey);
  }
  const requestPromise = (async () => {
    try {
      const response = await fetchWithBackoff(input, init, retries);
      if (response.ok) {
        cache.set(cacheKey, {
          response: response.clone(),
          timestamp: Date.now()
        });
        enforceCacheSize();
      }
      return response;
    } finally {
      inFlight.delete(cacheKey);
    }
  })();
  inFlight.set(cacheKey, requestPromise);
  await requestPromise;
}
