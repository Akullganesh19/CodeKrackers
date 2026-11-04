/**
 * 🛸 Oracle: Predictive Intelligence Engine
 * Anticipates user actions and pre-fetches or pre-computes data before requested.
 */

const oracleCache = new Map<string, { promise: Promise<Response>, expiry: number }>();

export const Oracle = {
  /**
   * Predicts and prefetches API data based on user intent (e.g., hovering or login).
   */
  prefetch: (url: string, token: string | null) => {
    if (!token) return;
    if (typeof window === 'undefined') return;

    // Normalize URL
    const urlObj = new URL(url, window.location.origin);
    const urlStr = urlObj.toString();

    if (oracleCache.has(urlStr)) {
      const cached = oracleCache.get(urlStr)!;
      if (cached.expiry > Date.now()) return;
    }

    const promise = fetch(urlStr, {
      headers: { 'Authorization': `Bearer ${token}` }
    }).then(res => {
      if (!res.ok) throw new Error('Prediction fetch failed');
      return res;
    }).catch(err => {
      oracleCache.delete(urlStr);
      throw err;
    });

    // 15 second TTL to prevent stale predictions
    oracleCache.set(urlStr, { promise, expiry: Date.now() + 15000 });
  },

  /**
   * Intercepts standard fetch calls. If Oracle has already predicted and pre-fetched
   * the request, it instantly resolves from the prediction cache.
   */
  install: () => {
    if (typeof window === 'undefined') return;
    if ((window as unknown as Record<string, unknown>).__oracle_installed) return;
    (window as unknown as Record<string, unknown>).__oracle_installed = true;

    const originalFetch = window.fetch;
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      let urlStr = '';
      let method = 'GET';

      if (input instanceof Request) {
        urlStr = input.url;
        method = input.method;
      } else {
        urlStr = input.toString();
        method = init?.method || 'GET';
      }

      // Normalize requested URL to match prefetch keys
      try {
        urlStr = new URL(urlStr, window.location.origin).toString();
      } // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
    catch (e: any) {
        // Ignore invalid URLs
      }

      if (method === 'GET' && oracleCache.has(urlStr)) {
        const cached = oracleCache.get(urlStr)!;
        if (cached.expiry > Date.now()) {
          try {
            const res = await cached.promise;
            // Return clone so response body can be consumed by the actual caller
            return res.clone();
          } // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
    catch (e: any) {
            // Degrade gracefully to normal fetch if prediction failed
            return originalFetch(input, init);
          }
        } else {
          oracleCache.delete(urlStr);
        }
      }

      return originalFetch(input, init);
    };
  }
};
