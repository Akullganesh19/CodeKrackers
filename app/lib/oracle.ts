// app/lib/oracle.ts

// Global module-level cache to ensure cross-component coalescing and survival across unmounts.
const predictionCache: Record<string, Promise<Response>> = {};

export const Oracle = {
  /**
   * Pre-computes the SMS scan when the user types or pastes text.
   * This sends the request in the background, caching the Promise.
   */
  preComputeScan: (text: string, token: string): void => {
    const trimmed = text.trim();
    if (!trimmed) return;

    // Use the trimmed text as the cache key
    const key = `scan:${trimmed}`;

    if (key in predictionCache) {
      return; // Already pre-computing or pre-computed
    }

    // Start the background fetch
    const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: trimmed })
    }).then((res) => {
      // If the HTTP response is not ok (e.g. 500), throw to trigger the catch block
      if (!res.ok) {
        throw new Error(`HTTP Error: ${res.status}`);
      }
      return res;
    }).catch((err) => {
      // On failure, delete the failed entry from the cache so that a manual retry
      // will trigger a fresh network request. Return a graceful fallback (mocking 500 response).
      delete predictionCache[key];
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    });

    predictionCache[key] = fetchPromise;
  },

  /**
   * Resolves a pre-computed prediction if it exists in the cache.
   * Always clones the response to prevent "body stream already read" errors.
   */
  resolvePrediction: async (text: string): Promise<Response | null> => {
    const trimmed = text.trim();
    if (!trimmed) return null;

    const key = `scan:${trimmed}`;
    if (key in predictionCache) {
      const res = await predictionCache[key];
      if (res.ok) {
        return res.clone();
      }
    }
    return null;
  },

  /**
   * Clears the prediction cache for a specific text or entirely.
   */
  clearPrediction: (text?: string) => {
    if (text) {
      const key = `scan:${text.trim()}`;
      delete predictionCache[key];
    } else {
      // Clear all
      for (const key in predictionCache) {
        delete predictionCache[key];
      }
    }
  }
};
