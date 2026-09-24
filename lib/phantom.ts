export function initPhantomInfrastructure() {
  if (typeof window === 'undefined') return;
  // @ts-expect-error global aug
  if (window.__phantomInitialized) return;
  // @ts-expect-error global aug
  window.__phantomInitialized = true;

  const originalFetch = window.fetch;
  const inFlight = new Map<string, Promise<Response>>();
  const cache = new Map<string, { buffer: ArrayBuffer, timestamp: number, headers: Headers, status: number, statusText: string }>();
  const CACHE_TTL = 1000 * 60 * 5; // 5 minutes

  // Periodic cache cleanup
  setInterval(() => {
    const now = Date.now();
    cache.forEach((value, key) => {
      if (now - value.timestamp >= CACHE_TTL) {
        cache.delete(key);
      }
    });
  }, 1000 * 60);

  window.fetch = async function (input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    let url = '';
    let method = 'GET';
    let authHeader = '';

    if (typeof input === 'string') {
      url = input;
    } else if (input instanceof URL) {
      url = input.toString();
    } else if (input instanceof Request) {
      url = input.url;
      method = input.method;
      authHeader = input.headers.get('Authorization') || input.headers.get('authorization') || '';
    }

    if (init?.method) method = init.method.toUpperCase();

    if (init?.headers) {
      if (init.headers instanceof Headers) {
        authHeader = init.headers.get('Authorization') || init.headers.get('authorization') || authHeader;
      } else if (Array.isArray(init.headers)) {
        const authItem = init.headers.find(h => h[0].toLowerCase() === 'authorization');
        if (authItem) authHeader = authItem[1];
      } else {
        const headerRecord = init.headers as Record<string, string>;
        const authKey = Object.keys(headerRecord).find(k => k.toLowerCase() === 'authorization');
        if (authKey) authHeader = headerRecord[authKey];
      }
    }

    if (method !== 'GET') {
      return originalFetch.call(window, input, init);
    }

    const cacheKey = `${method}:${url}:${authHeader}`;

    if (inFlight.has(cacheKey)) {
      console.log(`[Phantom] Coalesced duplicate request to ${url}`);
      const coalescedPromise = inFlight.get(cacheKey)!;
      const res = await coalescedPromise;
      return res.clone();
    }

    const cached = cache.get(cacheKey);
    const now = Date.now();

    if (cached && (now - cached.timestamp < CACHE_TTL)) {
      if (now - cached.timestamp > 30000) {
        console.log(`[Phantom] Stale-while-revalidate for ${url}`);
        originalFetch.call(window, input, init)
          .then(async (res: Response) => {
            if (res.ok) {
              const resClone = res.clone();
              const buffer = await resClone.arrayBuffer();
              cache.set(cacheKey, {
                buffer,
                timestamp: Date.now(),
                headers: resClone.headers,
                status: resClone.status,
                statusText: resClone.statusText
              });
            }
          })
          .catch(() => {});
      } else {
        console.log(`[Phantom] Cache hit for ${url}`);
      }
      return new Response(cached.buffer.slice(0), {
        status: cached.status,
        statusText: cached.statusText,
        headers: cached.headers
      });
    }

    const fetchPromise = originalFetch.call(window, input, init)
      .then((res: Response) => {
        if (res.ok) {
          const resCloneForCache = res.clone();
          resCloneForCache.arrayBuffer().then((buffer) => {
            cache.set(cacheKey, {
              buffer,
              timestamp: Date.now(),
              headers: resCloneForCache.headers,
              status: resCloneForCache.status,
              statusText: resCloneForCache.statusText
            });
          }).catch(() => {});
        }
        return res;
      })
      .finally(() => {
        inFlight.delete(cacheKey);
      });

    inFlight.set(cacheKey, fetchPromise);

    const finalRes = await fetchPromise;
    return finalRes.clone();
  };
}
