/**
 * ORACLE PREDICTIVE ENGINE 🔮
 * Anticipates user behavior and pre-computes data before it's explicitly requested.
 */

const prefetchCache: Record<string, Promise<any> | any> = {};

export const Oracle = {
  /**
   * Pre-computes the SMS/Text scan result in the background.
   * By the time the user clicks "Analyze", the data is already fetched.
   */
  preComputeScan: (text: string, token: string) => {
    const trimmed = text.trim();
    if (trimmed.length < 15) return; // Too short to predict

    const cacheKey = `scan_${trimmed}`;
    if (cacheKey in prefetchCache) return; // Already computing or computed

    console.log(`[Oracle 🔮] Anticipating scan for text: "${trimmed.substring(0, 20)}..."`);

    const fetchPromise = fetch('http://localhost:8000/api/analytics/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ text: trimmed })
    })
    .then(async res => {
      if (!res.ok) {
          throw new Error('Prefetch failed');
      }
      return await res.json();
    })
    .catch(err => {
      console.error(`[Oracle 🔮] Prefetch failed:`, err);
      delete prefetchCache[cacheKey]; // Clear on fail so normal flow can retry
      return { _error: true };
    });

    prefetchCache[cacheKey] = fetchPromise;

    fetchPromise.then(data => {
        if (!data._error) {
           prefetchCache[cacheKey] = data;
        }
    });
  },

  /**
   * Resolves a prediction if it exists, otherwise returns null.
   */
  resolvePrediction: async (text: string) => {
    const cacheKey = `scan_${text.trim()}`;
    if (cacheKey in prefetchCache) {
      console.log(`[Oracle 🔮] Prophecy fulfilled! Serving 0ms cached result for scan.`);
      const result = await prefetchCache[cacheKey];
      if (result._error) return null; // Fallback to normal flow if prefetch failed
      return result;
    }
    return null;
  }
};
