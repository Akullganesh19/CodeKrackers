const CACHE_TTL_MS = 5 * 60 * 1000;
const MAX_CACHE_SIZE = 100;

interface CacheEntry {
  response: Response;
  timestamp: number;
  revalidating: boolean;
}

const cache = new Map<string, CacheEntry>();
const inFlight = new Map<string, Promise<Response>>();

const IDEMPOTENT_METHODS = ['GET', 'HEAD', 'OPTIONS', 'PUT', 'DELETE'];

function evictIfNecessary() {
  if (cache.size >= MAX_CACHE_SIZE) {
    const oldestKey = Array.from(cache.entries()).sort((a, b) => a[1].timestamp - b[1].timestamp)[0][0];
    cache.delete(oldestKey);
  }
}

async function fetchWithRetry(req: Request, retries = 3, delay = 500): Promise<Response> {
  let lastResponse: Response | null = null;

  for (let i = 0; i <= retries; i++) {
    try {
      const response = await fetch(req.clone());
      lastResponse = response;

      if (!response.ok && response.status >= 500) {
        if (i < retries && IDEMPOTENT_METHODS.includes(req.method.toUpperCase())) {
          await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
          continue;
        }
      }
      return response;
    } catch (err) {
      if (i < retries && IDEMPOTENT_METHODS.includes(req.method.toUpperCase())) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
        continue;
      }
      throw err;
    }
  }

  if (lastResponse) return lastResponse;
  throw new Error("Fetch failed");
}

export async function phantomFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const req = new Request(input, init);
  const authHeader = req.headers.get('Authorization') || '';
  const key = `${req.method}:${req.url}:${authHeader}`;
  const isGET = req.method.toUpperCase() === 'GET';

  if (isGET) {
    const cached = cache.get(key);
    if (cached) {
      const isStale = Date.now() - cached.timestamp > CACHE_TTL_MS;
      if (!isStale) {
        console.log(`[phantomFetch] Cache hit for ${key} (stale: ${isStale})`); return cached.response.clone();
      }

      if (!cached.revalidating) {
        cached.revalidating = true;
        executeFetch(req, key, true).finally(() => { cached.revalidating = false; }).catch(console.error);
      }
      return cached.response.clone();
    }

    if (inFlight.has(key)) {
      const promise = inFlight.get(key)!;
      console.log(`[phantomFetch] Coalesced request for ${key}`); const res = await promise;
      return res.clone();
    }
  }


  if (req.method.toUpperCase() !== 'GET') {
    // Invalidate cache for mutations on the same URL path (naive heuristic)
    // Note: Since cache key contains method, we iterate and delete GET keys for this URL.
    for (const [k, v] of cache.entries()) {
      if (k.startsWith(`GET:${req.url}`)) {
        cache.delete(k);
        console.log(`[phantomFetch] Invalidated cache for ${k} due to mutation`);
      }
    }
  }

  return executeFetch(req, key, false);
}

async function executeFetch(req: Request, key: string, isRevalidating: boolean): Promise<Response> {
  const isGET = req.method.toUpperCase() === 'GET';

  const promise = fetchWithRetry(req)
    .then(response => {
      if (isGET && response.ok) {
        evictIfNecessary();
        cache.set(key, {
          response: response.clone(),
          timestamp: Date.now(),
          revalidating: false
        });
      } else if (isGET && !response.ok) {
        // Ensure non-2xx responses are not permanently cached
        cache.delete(key);
      }
      return response;
    })
    .finally(() => {
      if (!isRevalidating && isGET) {
        inFlight.delete(key);
      }
    });

  if (!isRevalidating && isGET) {
    inFlight.set(key, promise);
  }

  const res = await promise;
  return res.clone();
}
