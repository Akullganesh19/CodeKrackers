/**
 * phantomFetch - Invisible Infrastructure for Network Requests
 * Handles request coalescing (in-flight deduplication), transparent TTL caching, and exponential backoff retries.
 */

interface FetchOptions extends RequestInit {
  ttl?: number; // Time to live in ms (default 0 - no cache)
  retries?: number; // Number of retries (default 0)
  backoff?: number; // Backoff multiplier in ms (default 1000)
}

const inFlight = new Map<string, Promise<Response>>();
const cache = new Map<string, { response: Response; expires: number }>();

function generateCacheKey(input: RequestInfo | URL, init?: RequestInit): string {
  let urlStr = '';
  if (typeof input === 'string') {
    urlStr = input;
  } else if (input instanceof URL) {
    urlStr = input.toString();
  } else if (input && typeof input === 'object' && 'url' in input) {
    urlStr = input.url;
  }

  const method = init?.method || 'GET';
  const body = init?.body ? String(init.body) : '';
  return `${method}:${urlStr}:${body}`;
}

export async function phantomFetch(input: RequestInfo | URL, init?: FetchOptions): Promise<Response> {
  const { ttl = 0, retries = 0, backoff = 1000, ...fetchInit } = init || {};
  const cacheKey = generateCacheKey(input, fetchInit);
  const method = fetchInit.method?.toUpperCase() || 'GET';

  // 1. Check Cache
  if (ttl > 0 && method === 'GET') {
    const cached = cache.get(cacheKey);
    if (cached && cached.expires > Date.now()) {
      return cached.response.clone();
    }
  }

  // 2. Request Coalescing (In-flight deduplication)
  if (method === 'GET' && inFlight.has(cacheKey)) {
    const promise = inFlight.get(cacheKey)!;
    const res = await promise;
    return res.clone();
  }

  // 3. Execution with Retries
  const execute = async (attempt: number): Promise<Response> => {
    try {
      const res = await fetch(input, fetchInit);

      // Do not cache non-2xx responses or treat them as successful if retrying
      if (!res.ok && attempt < retries) {
        throw new Error(`HTTP Error ${res.status}`);
      }

      return res;
    } catch (err) {
      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, backoff * Math.pow(2, attempt)));
        return execute(attempt + 1);
      }
      throw err;
    }
  };

  const requestPromise = execute(0).then(res => {
    // Only cache if successful response
    if (res.ok && ttl > 0 && method === 'GET') {
      cache.set(cacheKey, {
        response: res.clone(),
        expires: Date.now() + ttl,
      });
    }
    return res;
  }).catch(err => {
    throw err;
  }).finally(() => {
    if (method === 'GET') {
      inFlight.delete(cacheKey);
    }
  });

  if (method === 'GET') {
    inFlight.set(cacheKey, requestPromise);
  }

  const res = await requestPromise;
  return res.clone();
}
