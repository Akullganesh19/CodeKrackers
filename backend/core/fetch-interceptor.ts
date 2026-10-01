let isInitialized = false;

export function initializeFetchInterceptor() {
  if (typeof window === 'undefined' || isInitialized) return;
  isInitialized = true;

  const originalFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();
  const cache = new Map<string, { cloneRes: Response; timestamp: number }>();
  const CACHE_TTL = 2000; // 2 seconds TTL to prevent rapid re-fetching on mount

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    let url: string;
    let method = 'GET';
    let reqHeaders: Headers;

    if (input instanceof Request) {
      url = input.url;
      method = input.method || 'GET';
      reqHeaders = new Headers(input.headers);
    } else {
      url = input.toString();
      reqHeaders = new Headers();
    }

    if (init && init.method) {
      method = init.method;
    }
    if (init && init.headers) {
      reqHeaders = new Headers(init.headers);
    }

    if (method.toUpperCase() !== 'GET') {
      return originalFetch(input, init);
    }

    // Build a deterministic key based on URL and Headers to prevent data spillage
    const headersObj: Record<string, string> = {};
    reqHeaders.forEach((value, key) => {
      headersObj[key.toLowerCase()] = value;
    });
    const key = url + '|' + JSON.stringify(headersObj);

    // 1. Return from cache if fresh
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.cloneRes.clone();
    }

    // 2. Coalesce in-flight requests (Note: we don't handle AbortSignals to prevent complex abort propagation bugs;
    // this means if a component aborts, it won't abort the network request if another is coalesced onto it, which is safer.)
    if (inFlight.has(key)) {
      const promise = inFlight.get(key)!;
      try {
        const res = await promise;
        return res.clone();
      } catch (err) {
        throw err;
      }
    }

    // 3. Execute original fetch
    // We execute the fetch and cache the clone WITHOUT awaiting the body reading,
    // preserving the standard fetch behavior (resolving when headers arrive).
    const promise = originalFetch(input, init).then((res) => {
      // Clone it immediately so we can serve the clone from cache next time
      const cloneToCache = res.clone();
      cache.set(key, {
        cloneRes: cloneToCache,
        timestamp: Date.now()
      });
      return res;
    }).finally(() => {
      inFlight.delete(key);
    });

    inFlight.set(key, promise);

    const res = await promise;
    return res.clone();
  };
}
