'use client'

export const Oracle = (() => {
  const cache: Record<string, Promise<Response>> = {};
  const MAX_CACHE_SIZE = 10;

  const preComputeScan = (text: string, token: string) => {
    if (!text || text.length < 5) return;

    // Cache key based on text
    const cacheKey = text.trim();
    if (cacheKey in cache) return; // Already computing or computed

    // Enforce eviction policy
    const keys = Object.keys(cache);
    if (keys.length >= MAX_CACHE_SIZE) {
      delete cache[keys[0]]; // Remove oldest
    }

    const scanPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: cacheKey })
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        return res;
      })
      .catch(err => {
        // Delete on failure so we don't cache failed requests
        delete cache[cacheKey];
        // Don't re-throw to avoid unhandled promise rejection in background
        return null;
      });

    // We store the promise itself, but cast it as Promise<Response> for the cache type
    // The catch block returning null means we need to handle it when resolving
    cache[cacheKey] = scanPromise as unknown as Promise<Response>;
  };

  const getScanResult = async (text: string): Promise<Response | null> => {
    const cacheKey = text.trim();
    if (cacheKey in cache) {
      try {
        const responsePromise = cache[cacheKey];
        const response = await responsePromise;
        delete cache[cacheKey];

        if (!response) {
          return null; // Handle the case where the background promise caught an error
        }

        const cloned = response.clone();
        return cloned;
      } catch (e) {
        delete cache[cacheKey];
        return null;
      }
    }
    return null;
  };

  return { preComputeScan, getScanResult };
})();
