export type PhantomFetchOptions = RequestInit & {
  /** Time to live in milliseconds. Default is 60000 (1 minute). Set to 0 to disable caching (only coalescing). */
  ttl?: number;
};

type CacheEntry = {
  promise: Promise<Response>;
  timestamp: number;
};

const cache: Record<string, CacheEntry> = {};
const inFlight: Record<string, Promise<Response>> = {};

export async function phantomFetch(
  input: RequestInfo | URL,
  init?: PhantomFetchOptions
): Promise<Response> {
  const ttl = init?.ttl !== undefined ? init.ttl : 60000;

  // 1. Extract URL string correctly to avoid "[object Request]"
  let urlStr = '';
  if (typeof input === 'string') {
    urlStr = input;
  } else if ('url' in input) {
    urlStr = input.url;
  } else {
    urlStr = input.toString();
  }

  const method = init?.method?.toUpperCase() || 'GET';

  // 2. We only coalesce and cache GET requests by default
  if (method !== 'GET') {
    return fetch(input, init);
  }

  // 3. Extract and serialize headers securely
  let headersObj: Record<string, string> = {};
  if (init?.headers) {
    if (init.headers instanceof Headers) {
      headersObj = Object.fromEntries(init.headers.entries());
    } else if (Array.isArray(init.headers)) {
      headersObj = Object.fromEntries(init.headers);
    } else {
      headersObj = init.headers as Record<string, string>;
    }
  }

  const cacheKey = `${urlStr}|${JSON.stringify(headersObj)}`;
  const now = Date.now();

  // 4. Check Cache (TTL-based)
  if (cacheKey in cache) {
    const entry = cache[cacheKey];
    if (now - entry.timestamp < ttl) {
      // 5. Clone response before consuming to avoid "body stream already read"
      try {
        const res = await entry.promise;
        return res.clone();
      } catch (err) {
        // If the cached promise fails, we fall through and retry
        delete cache[cacheKey];
      }
    } else {
      // Evict expired
      delete cache[cacheKey];
    }
  }

  // 6. Check In-Flight (Request Coalescing)
  if (cacheKey in inFlight) {
    try {
      const res = await inFlight[cacheKey];
      return res.clone();
    } catch (err) {
      // If the in-flight request fails, we fall through and retry
    }
  }

  // 7. Perform the actual Fetch
  const fetchPromise = fetch(input, init).then(res => {
    // Ensure non-2xx responses are not permanently cached
    if (!res.ok) {
      delete cache[cacheKey];
    }
    return res;
  }).catch(err => {
    delete inFlight[cacheKey];
    delete cache[cacheKey];
    throw err;
  });

  inFlight[cacheKey] = fetchPromise;

  try {
    const res = await fetchPromise;
    if (res.ok && ttl > 0) {
      cache[cacheKey] = {
        promise: fetchPromise,
        timestamp: Date.now()
      };
    }
    return res.clone();
  } finally {
    delete inFlight[cacheKey];
  }
}
