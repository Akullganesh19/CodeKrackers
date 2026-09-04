// 🛸 Predictive Intelligence Module
// This module provides predictive intelligence capabilities by caching unresolved client-side API fetch Promises.

type CacheKey = string;

const predictionCache: Record<CacheKey, Promise<unknown>> = {};

export const Oracle = {
    /**
     * Pre-computes an API request by firing the fetch early and caching the pending Promise.
     * @param url The API endpoint to pre-compute.
     * @param options Fetch options, including method, headers, and body.
     * @param keyOverride Optional override for the cache key.
     */
    preComputeScan: (url: string, options?: RequestInit, keyOverride?: string) => {
        const bodyStr = options?.body ? options.body.toString() : '';
        const defaultKey = `${options?.method || 'GET'}:${url}:${bodyStr}`;
        const key = keyOverride || defaultKey;

        // If a request for this exact payload is already in flight, do nothing.
        if (key in predictionCache) {
            return;
        }

        console.log(`[🛸 Oracle] Predicting user action. Pre-fetching: ${key}`);

        // Fire the fetch request and cache the Promise.
        const requestPromise = fetch(url, options)
            .then(res => res.clone()) // Clone to allow multiple reads if needed
            .catch(err => {
                console.error(`[🛸 Oracle] Pre-computation failed for ${key}`, err);
                return null as unknown as Response;
            });

        predictionCache[key] = requestPromise;

        // Clean up the cache after a short TTL to prevent stale data
        setTimeout(() => {
            if (key in predictionCache) {
                delete predictionCache[key];
            }
        }, 10000); // 10 seconds TTL
    },

    /**
     * Retrieves the pre-computed Promise if it exists.
     * @param url The API endpoint.
     * @param options Fetch options to match the cache key.
     * @param keyOverride Optional override for the cache key.
     */
    getScanResult: (url: string, options?: RequestInit, keyOverride?: string): Promise<Response> | null => {
        const bodyStr = options?.body ? options.body.toString() : '';
        const defaultKey = `${options?.method || 'GET'}:${url}:${bodyStr}`;
        const key = keyOverride || defaultKey;

        if (key in predictionCache) {
            console.log(`[🛸 Oracle] Cache hit! Returning pre-computed result for: ${key}`);
            const cachedPromise = predictionCache[key] as Promise<Response>;
            delete predictionCache[key]; // Consume the cache
            return cachedPromise.then(res => res.clone());
        }

        console.log(`[🛸 Oracle] Cache miss for: ${key}`);
        return null;
    }
};
