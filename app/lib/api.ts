const inFlight = new Map<string, Promise<Response>>();
const cache = new Map<string, { data: string; timestamp: number; headers: [string, string][] }>();

const CACHE_TTL = 5000; // 5 seconds for stale-while-revalidate

// Helper to reliably stringify Headers, Record<string, string>, or [string, string][]
function serializeHeaders(headers: HeadersInit | undefined): string {
  if (!headers) return '';
  const h = new Headers(headers);
  const entries: string[] = [];
  h.forEach((value, key) => {
    entries.push(`${key}:${value}`);
  });
  return entries.sort().join('|');
}

export async function dedupedFetch(url: string | URL | Request, options?: RequestInit): Promise<Response> {
  const urlStr = url.toString();

  // Only deduplicate and cache GET requests
  if (options && options.method && options.method !== 'GET') {
    return fetch(url, options);
  }

  // The cache key now robustly includes headers (like Authorization tokens)
  const cacheKey = urlStr + "||" + serializeHeaders(options?.headers);

  // 1. Check cache first (stale-while-revalidate pattern)
  const cached = cache.get(cacheKey);
  if (cached) {
    const isStale = Date.now() - cached.timestamp > CACHE_TTL;

    if (!isStale) {
      // Return cached response immediately if not stale
      return new Response(cached.data, {
        status: 200,
        headers: cached.headers
      });
    } else {
      // Trigger background refresh but still return stale data immediately
      // Do not await this
      fetch(url, options).then(async (res) => {
        if (res.ok) {
          const clone = res.clone();
          try {
            const textData = await clone.text();
            const headersObj: [string, string][] = [];
            res.headers.forEach((value, key) => headersObj.push([key, value]));
            cache.set(cacheKey, {
              data: textData,
              timestamp: Date.now(),
              headers: headersObj
            });
          } catch (e) { /* ignore */ }
        }
      }).catch(() => { /* ignore */ });

      return new Response(cached.data, {
        status: 200,
        headers: cached.headers
      });
    }
  }

  // 2. Request Coalescing: return in-flight promise if it exists
  if (inFlight.has(cacheKey)) {
    return inFlight.get(cacheKey)!.then(res => res.clone());
  }

  // 3. Start a new fetch
  const promise = fetch(url, options).then(async (res) => {
    // We only cache successful GET responses
    if (res.ok) {
      const cloneToRead = res.clone();
      // Read body asynchronously without blocking the original response from returning
      cloneToRead.text().then(textData => {
        const headersObj: [string, string][] = [];
        res.headers.forEach((value, key) => {
          headersObj.push([key, value]);
        });
        cache.set(cacheKey, {
          data: textData,
          timestamp: Date.now(),
          headers: headersObj
        });
      }).catch(() => { /* Ignore errors writing to cache */ });
    }
    return res;
  }).finally(() => {
    inFlight.delete(cacheKey);
  });

  inFlight.set(cacheKey, promise);

  return promise.then(res => res.clone());
}
