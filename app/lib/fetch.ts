export const CACHE_TTL_MS = 1000 * 60; // 1 minute default TTL

interface CacheEntry {
  promise: Promise<Response>;
  timestamp: number;
}

const cache: Record<string, CacheEntry> = {};

function generateCacheKey(url: string | URL | globalThis.Request, options?: RequestInit): string {
  const urlStr = typeof url === 'string' ? url : 'url' in url ? url.url : url.toString();
  if (!options) return urlStr;

  let headersObj: Record<string, string> = {};
  if (options.headers instanceof Headers) {
    headersObj = Object.fromEntries(options.headers.entries());
  } else if (options.headers) {
    headersObj = options.headers as Record<string, string>;
  }

  // Combine URL, method, and serialized headers
  return JSON.stringify({
    url: urlStr,
    method: options.method || 'GET',
    headers: headersObj,
  });
}

/**
 * phantomFetch is a global caching and request coalescing wrapper around fetch.
 * - If multiple calls to the same URL+options occur while one is in-flight, they share the promise.
 * - Resolves to cloned Response objects to prevent 'body stream already read' errors.
 * - On failure, it returns a 500 fallback Response to degrade gracefully.
 */
export async function phantomFetch(
  url: string | URL | globalThis.Request,
  options?: RequestInit,
  ttlMs: number = CACHE_TTL_MS
): Promise<Response> {
  // Only cache GET requests (or default method requests)
  if (options?.method && options.method.toUpperCase() !== 'GET') {
    return fetch(url, options);
  }

  const cacheKey = generateCacheKey(url, options);
  const now = Date.now();
  const existing = cache[cacheKey];

  if (existing !== undefined) {
    if (now - existing.timestamp < ttlMs) {
      try {
        const response = await existing.promise;
        return response.clone();
      } catch (err) {
        // Should be caught by the cache promise's catch block, but fallback just in case
      }
    } else {
      // Evict stale entry
      delete cache[cacheKey];
    }
  }

  // Create a new request promise that catches its own errors
  const promise = fetch(url, options)
    .then((res) => {
      // Must clone before returning so subsequent users of the promise can clone it
      return res.clone();
    })
    .catch((err) => {
      // On failure, remove from cache so the next call tries again
      delete cache[cacheKey];
      console.error(`[phantomFetch] Request failed for ${cacheKey}`, err);
      // Fallback response to avoid unhandled rejections
      return new Response(JSON.stringify({ error: "phantomFetch request failed", details: String(err) }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

  cache[cacheKey] = {
    promise,
    timestamp: now
  };

  const response = await promise;
  return response.clone();
}
