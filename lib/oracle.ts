// @/lib/oracle.ts

interface OracleCache {
  [key: string]: Promise<Response>;
}

// Global cache to persist across re-renders
const globalCache: OracleCache = {};
const debounceTimers: { [key: string]: NodeJS.Timeout } = {};

export const Oracle = {
  /**
   * Predictively pre-computes an API request by fetching it in the background.
   * Debounces identical requests to prevent spamming.
   */
  preComputeScan: (
    url: string,
    options?: RequestInit,
    debounceMs: number = 500,
    keyOverride?: string
  ) => {
    // Determine static debounce key to prevent dynamic input keystrokes from creating new timers
    const cacheKey = keyOverride || `${url}:${options?.body ? String(options.body) : ''}`;
    const debounceKey = url; // Key debounce timer by static URL

    if (debounceTimers[debounceKey]) {
      clearTimeout(debounceTimers[debounceKey]);
    }

    debounceTimers[debounceKey] = setTimeout(() => {
      // Don't re-fetch if we already have a pending/completed promise for this exact body
      if (cacheKey in globalCache) {
        return;
      }

      // Initiate background fetch
      const promise = fetch(url, options);

      // Cache the promise. Add a silent catch to prevent unhandled rejections from crashing the app
      // Store the raw promise in cache.
      // We attach a silent catch to prevent unhandled rejection warnings in the background,
      // but we return the original promise to the cache so the awaiter can handle the error properly.
      globalCache[cacheKey] = promise;
      promise.catch(() => {
        // Remove from cache on failure so we can try again later
        delete globalCache[cacheKey];
      });
    }, debounceMs);
  },

  /**
   * Retrieves the pre-computed request if it exists, otherwise performs a standard fetch.
   */
  getScanResult: async (url: string, options?: RequestInit, keyOverride?: string): Promise<Response> => {
    const cacheKey = keyOverride || `${url}:${options?.body ? String(options.body) : ''}`;

    // Clear debounce timer in case the user clicked immediately before it fired
    const debounceKey = url;
    if (debounceTimers[debounceKey]) {
      clearTimeout(debounceTimers[debounceKey]);
    }

    // Check if we already precomputed this specific request
    if (cacheKey in globalCache) {
      const cachedPromise = globalCache[cacheKey];
      delete globalCache[cacheKey]; // Consume the prediction

      try {
         const res = await cachedPromise;
         // Clone the response so the body can be read
         return res.clone();
      } catch (err) {
         // Fallback to normal fetch if cached promise rejected
         return fetch(url, options);
      }
    }

    // Fallback: normal fetch
    return fetch(url, options);
  }
};
