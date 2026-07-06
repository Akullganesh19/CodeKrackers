export interface CacheEntry {
  response: Response;
  timestamp: number;
}

const cache: Record<string, CacheEntry> = {};
const inFlight = new Map<string, Promise<Response>>();

const CACHE_TTL_MS = 60000; // 1 minute

export async function phantomFetch(
  url: string,
  options?: RequestInit & { noCache?: boolean, ttl?: number }
): Promise<Response> {
  // Generate a cache key that includes headers if they exist
  let headersString = '';
  if (options?.headers) {
    if (options.headers instanceof Headers) {
      headersString = JSON.stringify(Object.fromEntries(options.headers.entries()));
    } else {
      headersString = JSON.stringify(options.headers);
    }
  }

  const cacheKey = `${url}|${options?.method?.toUpperCase() || 'GET'}|${headersString}`;

  const isGet = (options?.method?.toUpperCase() || 'GET') === 'GET';
  const noCache = options?.noCache || !isGet;
  const ttl = options?.ttl ?? CACHE_TTL_MS;

  // 1. Check Cache
  if (!noCache && cache[cacheKey] !== undefined) {
    const entry = cache[cacheKey];
    if (Date.now() - entry.timestamp < ttl) {
      // INSTRUMENTATION
      console.log(`🌀 [Phantom] Cache hit for ${url}`);
      return entry.response.clone();
    }
  }

  // 2. Request Coalescing (In-flight deduping)
  if (!noCache && inFlight.has(cacheKey)) {
    // INSTRUMENTATION
    console.log(`🌀 [Phantom] Request coalesced for ${url}`);
    const promise = inFlight.get(cacheKey)!;
    const response = await promise;
    return response.clone();
  }

  // 3. Perform Fetch
  // INSTRUMENTATION
  const startTime = Date.now();
  console.log(`🌀 [Phantom] Fetching ${url}`);

  const fetchPromise = fetch(url, options)
    .then(async (res) => {
      console.log(`🌀 [Phantom] Fetched ${url} in ${Date.now() - startTime}ms`);
      // Store in cache only if it's a successful GET request (unless specified otherwise)
      if (res.ok && !noCache) {
        cache[cacheKey] = {
          response: res.clone(),
          timestamp: Date.now(),
        };
      }
      return res;
    })
    .catch((err) => {
      throw err;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  if (!noCache) {
    inFlight.set(cacheKey, fetchPromise);
  }

  const response = await fetchPromise;
  return response.clone();
}
