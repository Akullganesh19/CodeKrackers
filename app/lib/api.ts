const inFlight = new Map<string, Promise<Response>>();
const cache = new Map<string, { response: Response; expiresAt: number }>();

const CACHE_TTL_MS = 5000; // 5 seconds TTL

export async function dedupedFetch(url: string | URL | Request, options?: RequestInit): Promise<Response> {
    const urlStr = url.toString();
    const method = options?.method?.toUpperCase() || 'GET';

    // Only coalesce and cache GET requests
    if (method !== 'GET') {
        return fetch(url, options);
    }

    const cacheKey = `${urlStr}-${JSON.stringify(options?.headers || {})}`;

    // 1. Return from Cache if valid
    const cached = cache.get(cacheKey);
    if (cached && Date.now() < cached.expiresAt) {
        // We do background revalidation if it's older than half TTL (stale-while-revalidate pattern)
        if (Date.now() > cached.expiresAt - (CACHE_TTL_MS / 2)) {
            // Fire and forget revalidation
            if (!inFlight.has(cacheKey)) {
                const promise = fetch(url, options).then(res => {
                    if (res.ok) {
                        cache.set(cacheKey, { response: res.clone(), expiresAt: Date.now() + CACHE_TTL_MS });
                    }
                    return res;
                }).finally(() => {
                    inFlight.delete(cacheKey);
                });
                inFlight.set(cacheKey, promise);
            }
        }
        return cached.response.clone();
    }

    // 2. Coalesce in-flight requests
    if (inFlight.has(cacheKey)) {
        const response = await inFlight.get(cacheKey)!;
        return response.clone();
    }

    // 3. Network Fetch
    const promise = fetch(url, options);
    inFlight.set(cacheKey, promise);

    try {
        const response = await promise;

        // Cache successful responses
        if (response.ok) {
            cache.set(cacheKey, {
                response: response.clone(),
                expiresAt: Date.now() + CACHE_TTL_MS
            });
        }

        return response.clone();
    } finally {
        inFlight.delete(cacheKey);
    }
}
