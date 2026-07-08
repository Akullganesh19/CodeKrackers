export interface PhantomFetchOptions extends RequestInit {
  /** Time to live for the cache in milliseconds */
  ttl?: number;
  /** Whether to bypass the cache entirely */
  bypassCache?: boolean;
}

interface CacheEntry {
  data: unknown;
  timestamp: number;
  headers: Record<string, string>;
  status: number;
  statusText: string;
  promise?: Promise<Response>;
}

// Global cache to survive component unmounts
const cache: Record<string, CacheEntry> = {};

/**
 * phantomFetch - An invisible infrastructure fetch wrapper providing:
 * 1. Request Coalescing: Identical in-flight requests share the same promise.
 * 2. Intelligent Caching: GET/HEAD responses are cached with a TTL.
 * 3. Graceful Fallback: Mimics standard fetch API.
 */
export async function phantomFetch(input: string | URL | Request, options: PhantomFetchOptions = {}): Promise<Response> {
  const { ttl = 60000, bypassCache = false, ...fetchOptions } = options;

  // Handle Request object input vs string URL
  let urlString = '';
  let method = fetchOptions.method || 'GET';

  if (input instanceof Request) {
    urlString = input.url;
    method = fetchOptions.method || input.method || 'GET';
  } else {
    urlString = input.toString();
  }

  method = method.toUpperCase();

  // Only cache GET and HEAD requests. For mutations, pass through.
  const isCacheable = method === 'GET' || method === 'HEAD';

  if (!isCacheable) {
    console.log(`[Phantom] Bypass (non-cacheable method ${method}): ${urlString}`);
    return fetch(input, fetchOptions);
  }

  // Create a stable cache key that includes the URL and relevant headers
  let headersKey = '';
  if (fetchOptions.headers) {
    if (fetchOptions.headers instanceof Headers) {
      headersKey = JSON.stringify(Object.fromEntries(fetchOptions.headers.entries()));
    } else {
      headersKey = JSON.stringify(fetchOptions.headers);
    }
  } else if (input instanceof Request) {
      headersKey = JSON.stringify(Object.fromEntries(input.headers.entries()));
  }

  const cacheKey = `${method}|${urlString}|${headersKey}`;

  // 1. Check cache (Stale-while-revalidate / TTL)
  const now = Date.now();
  const cached = cache[cacheKey];

  if (!bypassCache && cached !== undefined) {
    // If we have an in-flight request, coalesce! Wait for it to finish.
    if (cached.promise) {
      console.log(`[Phantom] Coalescing request for: ${urlString}`);
      try {
        const res = await cached.promise;
        return res.clone();
      } catch {
        // Fallthrough on error to attempt a real request
      }
    }

    // If cache is fresh, return it immediately
    if (now - cached.timestamp < ttl) {
      console.log(`[Phantom] Cache hit for: ${urlString}`);
      return new Response(JSON.stringify(cached.data), {
        status: cached.status,
        statusText: cached.statusText,
        headers: cached.headers
      });
    }
  }

  // 2. Network Request & Coalescing
  console.log(`[Phantom] Network fetch for: ${urlString}`);

  // Create the fetch promise
  const requestPromise = fetch(input, fetchOptions)
    .then(async (res) => {
      // Only cache successful JSON responses
      if (res.ok) {
        const clonedRes = res.clone();
        try {
          const data = await clonedRes.json();
          const responseHeaders: Record<string, string> = {};
          res.headers.forEach((value, key) => {
            responseHeaders[key] = value;
          });

          cache[cacheKey] = {
            data,
            timestamp: Date.now(),
            headers: responseHeaders,
            status: res.status,
            statusText: res.statusText
          };
        } catch {
          // If not JSON, we don't cache for now
        }
      }
      return res;
    })
    .catch((error) => {
      // Clean up cache entry on error so subsequent requests can try again
      delete cache[cacheKey];
      // Throw exactly like native fetch
      throw error;
    })
    .finally(() => {
      // Clear the pending promise so future requests use the cached data or trigger a new fetch
      if (cache[cacheKey] !== undefined && cache[cacheKey].promise === requestPromise) {
        cache[cacheKey].promise = undefined;
      }
    });

  // Store the promise in the cache for request coalescing
  if (cache[cacheKey] === undefined) {
    cache[cacheKey] = {
        data: null,
        timestamp: 0,
        headers: {},
        status: 200,
        statusText: 'OK',
        promise: requestPromise
    };
  } else {
    cache[cacheKey].promise = requestPromise;
  }

  // Await the promise and clone it so multiple awaiters can read the stream
  const finalRes = await requestPromise;
  return finalRes.clone();
}
