// Predictive intelligence cache for SMS scanning
// Maps a text string to an unresolved fetch Promise that returns a Response
const predictiveCache: Record<string, Promise<Response>> = {};
const MAX_CACHE_SIZE = 10;

export const Oracle = {
  /**
   * Predictively pre-computes the scan result for a given text.
   * This should be called defensively (e.g. debounced onChange).
   */
  preComputeScan: (text: string, token: string): void => {
    const key = text.trim();
    if (!key) return;

    // Avoid duplicate background fetches for the same text
    if (key in predictiveCache) return;

    // Eviction policy: prevent unbounded memory growth by limiting cache size
    const cacheKeys = Object.keys(predictiveCache);
    if (cacheKeys.length >= MAX_CACHE_SIZE) {
      delete predictiveCache[cacheKeys[0]]; // Remove oldest
    }

    console.log(`[Oracle] Predictively scanning: "${key.substring(0, 20)}..."`);

    const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    }).then(res => {
      // Fetch doesn't reject on HTTP errors, so we must explicitly check
      if (!res.ok) {
        throw new Error(`HTTP Error: ${res.status}`);
      }
      return res;
    }).catch(err => {
      console.warn(`[Oracle] Pre-computation failed for "${key.substring(0, 20)}..."`, err);
      // Clean up failed predictions so explicit actions trigger a fresh retry
      if (key in predictiveCache) {
        delete predictiveCache[key];
      }
      // Return a mocked 500 response as fallback to gracefully handle errors
      return new Response(JSON.stringify({ error: err.message }), { status: 500 });
    });

    predictiveCache[key] = fetchPromise;
  },

  /**
   * Retrieves the pre-computed scan result if available, or initiates a fresh fetch.
   * Ensures the cached Response is not re-used, preventing 'body stream already read' errors.
   */
  getScanResult: async (text: string, token: string): Promise<Response> => {
    const key = text.trim();
    if (!key) throw new Error("Empty text provided");

    if (key in predictiveCache) {
      console.log(`[Oracle] Cache HIT for "${key.substring(0, 20)}..."`);
      const promise = predictiveCache[key];
      // Immediately delete from cache so subsequent requests clone/fetch anew
      delete predictiveCache[key];

      const response = await promise;
      // Note: We return the response directly since we deleted it from cache.
      // If we didn't delete it, we'd need to `return response.clone()`.
      return response;
    }

    console.log(`[Oracle] Cache MISS for "${key.substring(0, 20)}...", fetching now.`);

    // Normal fetch if we didn't predict it
    return fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: key })
    });
  }
};
