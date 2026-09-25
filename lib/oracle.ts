type CacheKey = string;

interface OracleCache {
  [key: CacheKey]: Promise<Response>;
}

const cache: OracleCache = {};
const debounceTimers: Record<string, NodeJS.Timeout> = {};

export const Oracle = {
  /**
   * Pre-computes an API request in the background.
   * Debounces continuous input on the same endpoint.
   */
  preComputeScan: (
    url: string,
    options: { method?: string; headers?: Record<string, string>; body?: unknown; keyOverride?: string },
    debounceMs: number = 500
  ) => {
    const { method = 'GET', headers, body, keyOverride } = options;
    const bodyStr = body ? JSON.stringify(body) : '';
    const cacheKey = keyOverride || `${url}|${method}|${bodyStr}`;
    const debounceId = url; // Group debouncing by URL so typing resets it

    if (debounceTimers[debounceId]) {
      clearTimeout(debounceTimers[debounceId]);
    }

    // Only start a new prediction if there's actual body content (for scans)
    if (body && typeof body === 'object' && 'text' in body && typeof (body as {text: unknown}).text === 'string' && (body as {text: string}).text.trim().length < 10) {
        return; // Don't precompute for very short texts
    }

    debounceTimers[debounceId] = setTimeout(() => {
      if (cacheKey in cache) return;

      const promise = fetch(url, {
        method,
        headers,
        body: bodyStr || undefined
      });

      // Background error handling for cleanup without throwing unhandled rejection
      promise.catch(() => {
        delete cache[cacheKey];
      });

      cache[cacheKey] = promise;
    }, debounceMs);
  },

  /**
   * Retrieves the pre-computed promise if it exists, removing it from the cache.
   */
  getScanResult: (
    url: string,
    options: { method?: string; body?: unknown; keyOverride?: string }
  ): Promise<Response> | null => {
    const { method = 'GET', body, keyOverride } = options;
    const bodyStr = body ? JSON.stringify(body) : '';
    const cacheKey = keyOverride || `${url}|${method}|${bodyStr}`;

    if (cacheKey in cache) {
      const promise = cache[cacheKey];
      delete cache[cacheKey];
      return promise;
    }
    return null;
  }
};
