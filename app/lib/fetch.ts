export const globalCache = new Map<string, { promise: Promise<Response>, timestamp: number }>();

export async function phantomFetch(url: RequestInfo | URL, options?: RequestInit & { ttl?: number }): Promise<Response> {
    const isGet = !options?.method || options.method.toUpperCase() === 'GET';

    // Pass through non-GET requests immediately
    if (!isGet) {
        return fetch(url, options);
    }

    const urlString = typeof url === 'object' && 'url' in url ? url.url : url.toString();

    let headersObj: Record<string, string> = {};
    if (options?.headers) {
        if (options.headers instanceof Headers) {
            headersObj = Object.fromEntries(options.headers.entries());
        } else {
            headersObj = options.headers as Record<string, string>;
        }
    }

    const cacheKey = JSON.stringify({
        url: urlString,
        method: 'GET',
        headers: headersObj,
        body: options?.body ? options.body.toString() : null
    });

    const now = Date.now();
    const ttl = options?.ttl ?? 60000;

    // Check cache
    if (globalCache.has(cacheKey)) {
        const entry = globalCache.get(cacheKey)!;
        if (now - entry.timestamp < ttl) {
            try {
                const res = await entry.promise;
                return res.clone();
            } catch (err) {
                // If the cached promise fails, we fall through to fetch again
            }
        }
    }

    // Cache miss or expired/failed: execute fetch
    const fetchPromise = fetch(url, options).then(res => {
        // Do not permanently cache non-2xx HTTP responses (e.g. 500 errors)
        if (!res.ok) {
            globalCache.delete(cacheKey);
        }
        return res;
    }).catch(err => {
        // Ensure failed fetches don't leave lingering rejected promises in cache
        globalCache.delete(cacheKey);
        throw err;
    });

    globalCache.set(cacheKey, { promise: fetchPromise, timestamp: now });

    const res = await fetchPromise;
    // Always clone the response so callers can read the body multiple times across components
    return res.clone();
}
