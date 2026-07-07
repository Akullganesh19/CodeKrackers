export interface PhantomOptions extends RequestInit {
  ttl?: number; // Time to live in ms
  staleWhileRevalidate?: boolean; // Serve stale while refreshing in background
}

interface CacheEntry {
  response: Response;
  expiresAt: number;
  promise?: Promise<Response>;
}

// Global module-level cache for request coalescing across components
const cache = new Map<string, CacheEntry>();

export async function phantomFetch(url: string, options: PhantomOptions = {}): Promise<Response> {
  const ttl = options.ttl ?? 10000; // default 10 seconds
  const staleWhileRevalidate = options.staleWhileRevalidate ?? true;

  // Serialize headers securely as per memory guidelines
  let headersObj: Record<string, string> = {};
  if (options.headers) {
    if (options.headers instanceof Headers) {
      headersObj = Object.fromEntries(options.headers.entries());
    } else if (Array.isArray(options.headers)) {
      headersObj = Object.fromEntries(options.headers);
    } else {
      headersObj = options.headers as Record<string, string>;
    }
  }

  const cacheKey = `${url}-${options.method || 'GET'}-${JSON.stringify(options.body)}-${JSON.stringify(headersObj)}`;

  const now = Date.now();
  const cached = cache.get(cacheKey);

  // 1. STALE-WHILE-REVALIDATE: If we have an inflight background refresh but also have stale data, serve stale immediately.
  if (staleWhileRevalidate && cached && cached.response && cached.promise) {
    console.log(`[PhantomFetch] serving STALE cache for ${url} while background refreshing...`);
    return cached.response.clone();
  }

  // 2. COALESCING: If we have an in-flight request (and no stale data), wait on it
  if (cached && cached.promise) {
    console.log(`[PhantomFetch] coalescing request for ${url} with existing in-flight promise`);
    return cached.promise.then(res => res.clone());
  }

  // 3. CACHE HIT: If we have a valid cache, return a clone of it immediately
  if (cached && cached.expiresAt > now) {
    console.log(`[PhantomFetch] CACHE HIT for ${url} (expires in ${cached.expiresAt - now}ms)`);
    return cached.response.clone();
  }

  console.log(`[PhantomFetch] CACHE MISS for ${url}, fetching fresh data...`);

  // Define the fetch operation
  const doFetch = async () => {
    try {
      const response = await fetch(url, options);
      // We must clone the response before caching it because response body can only be read once
      const responseToCache = response.clone();

      cache.set(cacheKey, {
        response: responseToCache,
        expiresAt: Date.now() + ttl,
        promise: undefined,
      });
      return response;
    } catch (error) {
      // Return a 500 fallback instead of silently failing, as per memory guidelines
      const fallbackResponse = new Response(JSON.stringify({ error: "Background fetch failed" }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });

      // We don't cache the fallback, just return it so app handles it
      if (cached && cached.response) {
         // Keep stale data alive a bit longer if fetch failed
         cache.set(cacheKey, {
            response: cached.response,
            expiresAt: Date.now() + 5000,
            promise: undefined,
         });
      } else {
         cache.delete(cacheKey);
      }
      return fallbackResponse;
    }
  };

  const promise = doFetch();

  // 4. STALE-WHILE-REVALIDATE (first trigger): Serve stale data while fetching
  if (staleWhileRevalidate && cached && cached.response) {
     console.log(`[PhantomFetch] returning STALE cache for ${url} while triggering background refresh...`);
     cache.set(cacheKey, {
       ...cached,
       promise: promise.then(res => res.clone()), // keep track of the inflight request
     });
     // Don't await the promise, just return a clone of the stale data
     return cached.response.clone();
  }

  // Store the promise for request coalescing
  cache.set(cacheKey, {
    response: new Response(), // Dummy response, will be overwritten by doFetch
    expiresAt: 0,
    promise: promise.then(res => res.clone()), // Cache the promise of a clone
  });

  return promise;
}
