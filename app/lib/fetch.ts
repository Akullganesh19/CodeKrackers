export const CACHE_TTL = 30000; // 30 seconds

// We store the Promise of the response so that concurrent requests for the same URL
// can simply await the identical promise, achieving request coalescing.
const cache: Record<string, { promise: Promise<Response>; timestamp: number }> = {};

export async function phantomFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  // Only cache GET requests
  if (options.method && options.method.toUpperCase() !== 'GET') {
    return fetch(url, options);
  }

  // Create a unique key that accounts for the URL and authorization headers
  let authHeader = '';
  if (options.headers) {
    if (options.headers instanceof Headers) {
      authHeader = options.headers.get('Authorization') || '';
    } else if (Array.isArray(options.headers)) {
      const headerEntry = options.headers.find(
        (h) => h[0].toLowerCase() === 'authorization'
      );
      authHeader = headerEntry ? headerEntry[1] : '';
    } else {
      // Record<string, string>
      const headers = options.headers as Record<string, string>;
      const authKey = Object.keys(headers).find(
        (k) => k.toLowerCase() === 'authorization'
      );
      if (authKey) {
        authHeader = headers[authKey];
      }
    }
  }

  const cacheKey = `${url}|${authHeader}`;
  const now = Date.now();
  const cached = cache[cacheKey];

  if (cached !== undefined) {
    const isStale = now - cached.timestamp > CACHE_TTL;

    if (isStale) {
      // Trigger stale-while-revalidate in the background
      const fetchPromise = fetch(url, options)
        .then((res) => {
          if (!res.ok) {
             delete cache[cacheKey];
          }
          return res;
        })
        .catch((err) => {
          delete cache[cacheKey];
          // We don't want to swallow errors that might be awaited
          throw err;
        });

      cache[cacheKey] = { promise: fetchPromise, timestamp: now };

      // We must attach a catch handler to the SWR background promise so unhandled rejections
      // don't crash Next.js if there's no component awaiting it right now.
      fetchPromise.catch(() => {});
    }

    // Await the cached (or newly fired SWR) promise.
    // IMPORTANT: we must clone() the response because the body of a single response
    // can only be consumed once. Returning a clone allows multiple consumers to call .json()
    try {
      const res = await cached.promise;
      if (res && typeof res.clone === 'function') {
        return res.clone();
      }
      return res;
    } catch (e) {
      // If the cached promise fails, we fall back to a fresh fetch
      delete cache[cacheKey];
      return fetch(url, options);
    }
  }

  // No cache hit: perform standard fetch, but cache the promise for coalescing
  const fetchPromise = fetch(url, options)
    .then((res) => {
      if (!res.ok) {
        delete cache[cacheKey];
      }
      return res;
    })
    .catch((err) => {
      // Remove failed requests from cache immediately
      delete cache[cacheKey];
      throw err;
    });

  cache[cacheKey] = { promise: fetchPromise, timestamp: now };

  try {
    const res = await fetchPromise;
    if (res && typeof res.clone === 'function') {
      return res.clone();
    }
    return res;
  } catch (e) {
    throw e;
  }
}
