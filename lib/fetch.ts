// lib/fetch.ts

// Request Coalescing (Deduplication) for global window.fetch
// Multiple simultaneous GET requests for the same exact URL will share a single promise,
// returning the same response without making redundant network calls.

const inFlightRequests = new Map<string, Promise<Response>>();

if (typeof window !== 'undefined') {
  const originalFetch = window.fetch;

  window.fetch = async function (
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response> {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;

    // Check method accurately (handling Request objects too)
    let method = 'GET';
    if (init && init.method) {
        method = init.method.toUpperCase();
    } else if (input instanceof Request) {
        method = input.method.toUpperCase();
    }

    // Only coalesce GET requests without bodies
    const isCacheableMethod = method === 'GET';

    if (isCacheableMethod) {
      // Create a cache key using URL and headers (simplified)
      // In a real implementation we might hash the init object
      const cacheKey = `${url}`;

      if (inFlightRequests.has(cacheKey)) {
        console.debug(`[Phantom] Coalescing request for: ${url}`);
        const response = await inFlightRequests.get(cacheKey)!;
        // Clone the response so multiple callers can consume the body independently
        return response.clone();
      }

      const fetchPromise = originalFetch.apply(this, [input, init]).then(
        (response) => {
          // Keep the original in the cache to clone from, but we must return a clone here too
          // to ensure the original is never consumed before others clone it
          return response;
        }
      ).finally(() => {
        inFlightRequests.delete(cacheKey);
      });

      inFlightRequests.set(cacheKey, fetchPromise);

      const response = await fetchPromise;
      return response.clone();
    }

    return originalFetch.apply(this, [input, init]);
  };
}

export {};
