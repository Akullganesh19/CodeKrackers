export interface PhantomFetchOptions extends RequestInit {
  ttl?: number;
  retries?: number;
  backoffDelay?: number;
}

interface CacheEntry {
  promise: Promise<Response>;
  timestamp: number;
  ttl: number;
  data?: Response; // Store the resolved clone for SWR
}

const inFlight = new Map<string, Promise<Response>>();
const cache = new Map<string, CacheEntry>();

const IDEMPOTENT_METHODS = new Set(['GET', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']);

function getUrlString(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.toString();
  if (input && typeof input === 'object' && 'url' in input) {
    return (input as { url: string }).url;
  }
  return String(input);
}

function getAuthHeader(init?: RequestInit): string {
  if (!init || !init.headers) return '';
  const headers = new Headers(init.headers);
  return headers.get('Authorization') || '';
}

export const phantomFetch = async (input: RequestInfo | URL, init?: PhantomFetchOptions): Promise<Response> => {
  const url = getUrlString(input);
  const method = init?.method?.toUpperCase() || 'GET';

  if (method !== 'GET') {
    return doFetchWithRetries(input, init);
  }

  const authHeader = getAuthHeader(init);
  const cacheKey = `${method}:${url}:${authHeader}`;

  const cached = cache.get(cacheKey);
  const ttl = init?.ttl ?? 60000; // Default 60 seconds TTL for GET requests

  if (cached) {
    if (Date.now() - cached.timestamp < cached.ttl) {
      // Fresh hit
      if (cached.data) {
         return cached.data.clone();
      }
      const res = await cached.promise;
      return res.clone();
    } else {
      // Stale hit (SWR)
      // Fire request in background
      const backgroundPromise = doFetchWithRetries(input, init).then(res => {
        if (res.ok) {
           const cacheEntry = cache.get(cacheKey);
           if (cacheEntry) {
              cacheEntry.data = res.clone();
              cacheEntry.timestamp = Date.now();
              cacheEntry.promise = Promise.resolve(res.clone());
           } else {
              cache.set(cacheKey, { promise: Promise.resolve(res.clone()), timestamp: Date.now(), ttl, data: res.clone() });
           }
        } else {
           cache.delete(cacheKey);
        }
        return res;
      }).catch(err => {
        cache.delete(cacheKey);
      }).finally(() => {
        inFlight.delete(cacheKey);
      });
      inFlight.set(cacheKey, backgroundPromise as Promise<Response>);

      if (cached.data) {
        return cached.data.clone(); // Return stale data immediately
      }
    }
  }

  const inFlightPromise = inFlight.get(cacheKey);
  if (inFlightPromise) {
    const res = await inFlightPromise;
    return res.clone();
  }

  const promise = doFetchWithRetries(input, init).then(res => {
    if (!res.ok) {
      cache.delete(cacheKey);
    } else {
       const cacheEntry = cache.get(cacheKey);
       if (cacheEntry) {
         cacheEntry.data = res.clone();
       }
    }
    return res;
  }).catch(err => {
    cache.delete(cacheKey);
    throw err;
  }).finally(() => {
    inFlight.delete(cacheKey);
  });

  inFlight.set(cacheKey, promise);

  if (ttl > 0) {
    cache.set(cacheKey, { promise, timestamp: Date.now(), ttl });
  }

  const res = await promise;
  return res.clone();
};

async function doFetchWithRetries(input: RequestInfo | URL, init?: PhantomFetchOptions): Promise<Response> {
  const method = init?.method?.toUpperCase() || 'GET';
  let retries = IDEMPOTENT_METHODS.has(method) ? (init?.retries ?? 3) : 0;
  let delay = init?.backoffDelay ?? 500;

  while (true) {
    try {
      const res = await fetch(input, init);
      if (!res.ok && res.status >= 500 && retries > 0) {
        throw new Error(`HTTP Error: ${res.status}`);
      }
      return res;
    } catch (err) {
      if (retries <= 0) {
        throw err;
      }
      retries--;
      await new Promise(r => setTimeout(r, delay));
      delay *= 2;
    }
  }
}
